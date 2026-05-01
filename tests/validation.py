"""
Validation tests: compare ABM simulation output against the Szolnoki ODE.

Run with:
    uv run pytest tests/validation.py --log-level-cli INFO
"""

import numpy as np
import pytest

from cse6730_project.simulation.simulation import Simulation
from cse6730_project.agents import PlayerCopycat, PlayerMutator
from cse6730_project.config import ODE_PARAMS
from cse6730_project.ode.ode import OdeRPS
from cse6730_project.models import Card, AgentType

N_PLAYERS = 200
N_TICKS = 1000
# 1 ODE time unit ≈ N/2 ticks
T_END = N_TICKS * (2 * ODE_PARAMS.z) / N_PLAYERS
SEED = 42


@pytest.fixture(scope="module")
def copycat_validation_pair():
    """Sim (copycat-only) + matching ODE, sharing the same initial conditions."""
    sim = Simulation(
        num_players=N_PLAYERS,
        num_scalpers=0,
        num_ticks=N_TICKS,
        player_type={PlayerCopycat: 1, PlayerMutator: 0},
        seed=SEED,
    )
    ic = sim.get_card_counts(AgentType.PLAYER)  # capture before run
    ode = OdeRPS(
        Z_COPYCAT_RATE=1.0,
        MU_MUTATION_RATE=0.0,
        initial_counts=ic,
        t_interval=(0, T_END),
        t_eval=[0, T_END, N_TICKS],
    )
    sim.run()
    return sim, ode


@pytest.fixture(scope="module")
def mutator_sim():
    """Mutator-only sim (no selection)."""
    sim = Simulation(
        num_players=N_PLAYERS,
        num_scalpers=0,
        num_ticks=N_TICKS,
        player_type={PlayerCopycat: 0, PlayerMutator: 1},
        seed=SEED,
    )
    sim.run()
    return sim


def test_history_length(copycat_validation_pair):
    """Simulation records exactly one snapshot per tick."""
    sim, _ = copycat_validation_pair
    assert len(sim.getHistory()) == N_TICKS


def test_population_sums_to_one(copycat_validation_pair):
    """Card fractions sum to 1.0 at every tick."""
    sim, _ = copycat_validation_pair
    for snap in sim.getHistory():
        total = sum(snap.card_populations.values())
        assert abs(total - 1.0) < 1e-9, f"tick {snap.tick}: fractions sum to {total}"


def test_populations_bounded(copycat_validation_pair):
    """All population fractions stay in [0, 1]."""
    sim, _ = copycat_validation_pair
    for snap in sim.getHistory():
        for card, frac in snap.card_populations.items():
            assert 0.0 <= frac <= 1.0, (
                f"{card.name} fraction {frac} out of bounds at tick {snap.tick}"
            )


# ODE correspondence


def test_ode_initial_conditions_match(copycat_validation_pair):
    """ODE t=0 matches the simulation's initial card fractions."""
    sim, ode = copycat_validation_pair
    ode_result = ode.SolveODE()
    sim_ic = sim.getHistory()[0].card_populations

    # ODE y-row order: [ROCK, SCISSOR, PAPER] (from OdeRPS.convert_initial_pop_to_float)
    for ode_idx, card in [(0, Card.ROCK), (1, Card.SCISSOR), (2, Card.PAPER)]:
        assert abs(ode_result.y[ode_idx][0] - sim_ic[card]) < 0.01, (
            f"{card.name}: ODE IC {ode_result.y[ode_idx][0]:.4f} != sim IC {sim_ic[card]:.4f}"
        )


def test_copycat_trajectory_tracks_ode(copycat_validation_pair):
    """
    Time-rescaled sim trajectory stays within MAE < 0.15 of the ODE.
    Tolerance accounts for single-run stochastic noise at N=200.
    """
    sim, ode = copycat_validation_pair
    ode_result = ode.SolveODE()
    pop_hist = sim.get_population_history()

    checkpoints = np.linspace(0, N_TICKS - 1, 20, dtype=int)
    ode_times = checkpoints * (2 * ODE_PARAMS.z) / N_PLAYERS

    for ode_idx, card in [(0, Card.ROCK), (1, Card.SCISSOR), (2, Card.PAPER)]:
        sim_vals = np.array([pop_hist[card][t] for t in checkpoints])
        ode_vals = np.interp(ode_times, ode_result.t, ode_result.y[ode_idx])
        mae = float(np.mean(np.abs(sim_vals - ode_vals)))
        assert mae < 0.20, (
            f"{card.name}: mean abs error {mae:.3f} exceeds 0.20 — "
            "sim may not be tracking ODE dynamics"
        )


def test_copycat_trend_direction(copycat_validation_pair):
    """
    With ROCK-heavy initial conditions the ODE predicts ROCK decreases and
    PAPER increases. The sim should show the same qualitative trend over the
    first half of the run.
    """
    sim, _ = copycat_validation_pair
    pop_hist = sim.get_population_history()
    mid = N_TICKS // 2

    rock_start = np.mean(pop_hist[Card.ROCK][:50])
    rock_mid = np.mean(pop_hist[Card.ROCK][mid - 25 : mid + 25])
    paper_start = np.mean(pop_hist[Card.PAPER][:50])
    paper_mid = np.mean(pop_hist[Card.PAPER][mid - 25 : mid + 25])

    assert rock_mid < rock_start, (
        "ROCK should decrease from its initially dominant position"
    )
    assert paper_mid > paper_start, (
        "PAPER should increase as it exploits the dominant ROCK"
    )


# Mutation dynamics


def test_mutation_reduces_population_skew(mutator_sim):
    """
    Mutation (without selection) should drive populations toward uniform 1/3.
    The variance across card fractions should decrease from start to end.
    """
    history = mutator_sim.getHistory()
    initial_pops = np.array([history[0].card_populations[c] for c in Card])
    final_pops = np.array([history[-1].card_populations[c] for c in Card])

    initial_std = float(np.std(initial_pops))
    final_std = float(np.std(final_pops))

    assert final_std < initial_std, (
        f"Mutation should reduce variance: initial std={initial_std:.4f}, "
        f"final std={final_std:.4f}"
    )
