"""
Plotting tests: generate ODE and sim-vs-ODE comparison plots using config.py params.

These tests only assert that plot files are produced without error.
Quantitative validation lives in tests/validation.py.

Run all:
    uv run pytest tests/test_plots.py --log-cli-level INFO
"""

from pathlib import Path

import pytest

from cse6730_project.agents import PlayerCopycat, PlayerMutator
from cse6730_project.config import (
    NUM_PLAYERS,
    NUM_TICKS,
    ODE_PARAMS,
    RNG_SEED,
    SEED_DECK_WEIGHTS,
    ODE_SCALE,
)
from cse6730_project.models import AgentType, Card
from cse6730_project.ode.ode import OdeRPS
from cse6730_project.simulation.simulation import Simulation
from cse6730_project.visualization import ComparisonVisualizer, ODEVisualizer
from cse6730_project.games import GameOneCard, GameNineCard

# 1 ODE time unit
_T_END = NUM_TICKS / NUM_PLAYERS
_ODE_SCALE = ODE_SCALE


def test_ode_plot():
    """
    Solve the ODE with ODE_PARAMS from config and save a plot to plots/ode/.
    Uses SEED_DECK_WEIGHTS ratios as initial conditions.
    """
    ic = {card: int(w) for card, w in SEED_DECK_WEIGHTS.items()}

    ode = OdeRPS(
        Z_COPYCAT_RATE=ODE_PARAMS.z,
        MU_MUTATION_RATE=ODE_PARAMS.mu,
        initial_counts=ic,
        t_interval=(ODE_PARAMS.t_interval.start, ODE_PARAMS.t_interval.end),
        # use at least 500 eval points so the plot curve is smooth
        t_eval=[
            ODE_PARAMS.t_eval.start,
            ODE_PARAMS.t_eval.end,
            max(ODE_PARAMS.t_eval.step, 500),
        ],
    )
    result = ode.SolveODE()

    existing = set(Path("plots/ode").glob("*.png"))
    ODEVisualizer().save_fig_ode(result.t, result.y, simparams=None)
    new_files = set(Path("plots/ode").glob("*.png")) - existing

    assert new_files, "test_ode_plot: no new plot file written to plots/ode/"


def test_comparison_plot():
    """
    Run a copycat-only simulation with NUM_PLAYERS / NUM_TICKS from config,
    overlay on the matching ODE solution, and save the plot to plots/.

    Initial conditions for the ODE are taken from the simulation before it runs
    so both share identical starting fractions.
    """
    sim = Simulation(
        num_players=NUM_PLAYERS,
        num_scalpers=0,
        num_ticks=NUM_TICKS,
        seed=RNG_SEED,
        game_type=GameNineCard,
    )
    ic = sim.get_card_counts(AgentType.PLAYER)  # capture before run

    ode = OdeRPS(
        Z_COPYCAT_RATE=ODE_PARAMS.z,
        MU_MUTATION_RATE=ODE_PARAMS.mu,
        initial_counts=ic,
        t_interval=(0, _T_END * _ODE_SCALE),
        # match number of eval points to ticks so interpolation is accurate
        t_eval=[0, _T_END * _ODE_SCALE, NUM_TICKS],
    )

    sim.run()
    ode_result = ode.SolveODE()

    viz = ComparisonVisualizer()
    viz.plot_sim_vs_ode(sim, ode_result, num_players=NUM_PLAYERS, fname="comparison")
