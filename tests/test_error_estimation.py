"""
Error estimation: measure how closely the simulation's cumulative-average
trajectory tracks the ODE solution after rescaling both time axes to [0, 1].

Rationale
---------
The sim converges faster than the ODE in wall-clock / tick terms, so a 1-to-1
tick-vs-ODE-time comparison inflates apparent error near the end of the run.
Normalising both axes to [0, 1] aligns the *shapes* of the two trajectories
instead of their absolute time coordinates, which is the fair comparison for
an agent-based model that approximates ODE dynamics qualitatively.

Procedure
---------
1. Run sim + ODE with identical initial conditions.
2. Compute the normalised time axis for each:
       t_norm = (t - t[0]) / (t[-1] - t[0])
3. Interpolate the ODE fractions at every sim normalised-time point.
4. Compare the sim's cumulative time average against those interpolated ODE values.
5. Report per-card RMSE and MAE and assert both stay below MAX_RMSE / MAX_MAE.

Run:
    uv run pytest tests/test_error_estimation.py -v --log-cli-level INFO
"""

import logging
from pathlib import Path

import numpy as np
import pytest

from cse6730_project.config import NUM_PLAYERS, NUM_TICKS, ODE_PARAMS, ODE_SCALE, RNG_SEED
from cse6730_project.models import AgentType, Card
from cse6730_project.ode.ode import OdeRPS
from cse6730_project.simulation.simulation import Simulation
from cse6730_project.games import GameNineCard
from cse6730_project.visualization import ErrorVisualizer

logger = logging.getLogger(__name__)

# ODE row → Card mapping (matches OdeRPS.convert_initial_pop_to_float)
_ODE_CARD_ORDER = [Card.ROCK, Card.SCISSOR, Card.PAPER]

# Error thresholds — generous enough to tolerate single-run stochastic noise
MAX_RMSE = 0.08
MAX_MAE = 0.08

_T_END = NUM_TICKS / NUM_PLAYERS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise(arr: np.ndarray) -> np.ndarray:
    """Linearly rescale arr so that arr[0] -> 0 and arr[-1] -> 1."""
    span = arr[-1] - arr[0]
    if span == 0:
        raise ValueError("Cannot normalise a constant array.")
    return (arr - arr[0]) / span


def _cumulative_avg(values: list[float]) -> np.ndarray:
    a = np.asarray(values, dtype=float)
    return np.cumsum(a) / np.arange(1, len(a) + 1)


def _interpolate_ode_at_sim_times(
    ode_t_norm: np.ndarray,
    ode_y_row: np.ndarray,
    sim_t_norm: np.ndarray,
) -> np.ndarray:
    """Return ODE fractions interpolated at every sim normalised time point."""
    return np.interp(sim_t_norm, ode_t_norm, ode_y_row)


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sim_ode_pair():
    """Default-mix sim (copycats + mutators) + matching ODE, identical initial conditions."""
    sim = Simulation(
        num_players=NUM_PLAYERS,
        num_scalpers=0,
        num_ticks=NUM_TICKS,
        seed=RNG_SEED,
        game_type=GameNineCard,
    )
    ic = sim.get_card_counts(AgentType.PLAYER)

    ode = OdeRPS(
        Z_COPYCAT_RATE=ODE_PARAMS.z,
        MU_MUTATION_RATE=ODE_PARAMS.mu,
        initial_counts=ic,
        t_interval=(0, _T_END * ODE_SCALE),
        t_eval=[0, _T_END * ODE_SCALE, NUM_TICKS],
    )

    sim.run()
    ode_result = ode.SolveODE()
    return sim, ode_result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_normalised_rmse_per_card(sim_ode_pair):
    """
    After time-normalisation, the sim cumulative average must track the ODE
    trajectory with RMSE < MAX_RMSE for every card.
    """
    sim, ode_result = sim_ode_pair
    pop_hist = sim.get_population_history()
    n_ticks = len(sim.getHistory())

    t_sim_norm = _normalise(np.arange(n_ticks, dtype=float))
    t_ode_norm = _normalise(ode_result.t)

    for ode_idx, card in enumerate(_ODE_CARD_ORDER):
        sim_avg = _cumulative_avg(pop_hist[card])
        ode_at_sim = _interpolate_ode_at_sim_times(
            t_ode_norm, ode_result.y[ode_idx], t_sim_norm
        )
        rmse = float(np.sqrt(np.mean((sim_avg - ode_at_sim) ** 2)))
        logger.info("RMSE  %-10s %.4f  (threshold %.2f)", card.name, rmse, MAX_RMSE)
        assert rmse < MAX_RMSE, (
            f"{card.name}: RMSE {rmse:.4f} exceeds {MAX_RMSE} — "
            "sim cumulative average deviates too far from ODE trajectory"
        )


def test_normalised_mae_per_card(sim_ode_pair):
    """
    After time-normalisation, the sim cumulative average must track the ODE
    trajectory with MAE < MAX_MAE for every card.
    """
    sim, ode_result = sim_ode_pair
    pop_hist = sim.get_population_history()
    n_ticks = len(sim.getHistory())

    t_sim_norm = _normalise(np.arange(n_ticks, dtype=float))
    t_ode_norm = _normalise(ode_result.t)

    for ode_idx, card in enumerate(_ODE_CARD_ORDER):
        sim_avg = _cumulative_avg(pop_hist[card])
        ode_at_sim = _interpolate_ode_at_sim_times(
            t_ode_norm, ode_result.y[ode_idx], t_sim_norm
        )
        mae = float(np.mean(np.abs(sim_avg - ode_at_sim)))
        logger.info("MAE   %-10s %.4f  (threshold %.2f)", card.name, mae, MAX_MAE)
        assert mae < MAX_MAE, (
            f"{card.name}: MAE {mae:.4f} exceeds {MAX_MAE} — "
            "sim cumulative average deviates too far from ODE trajectory"
        )


def test_error_plot(sim_ode_pair):
    """
    plot_error() must write exactly three new PNGs to plots/error/:
      *_sim.png, *_error.png, *_combined.png
    """
    sim, ode_result = sim_ode_pair
    existing = set(Path("plots/error").glob("*.png"))
    ErrorVisualizer().plot_error(sim, ode_result, fname="error")
    new_files = set(Path("plots/error").glob("*.png")) - existing
    assert len(new_files) == 3, (
        f"Expected 3 new plot files in plots/error/, got {len(new_files)}: {new_files}"
    )


def test_per_card_error_summary(sim_ode_pair, capsys):
    """
    Print a human-readable error table; always passes — useful for tuning
    thresholds and spotting regressions quickly.
    """
    sim, ode_result = sim_ode_pair
    pop_hist = sim.get_population_history()
    n_ticks = len(sim.getHistory())

    t_sim_norm = _normalise(np.arange(n_ticks, dtype=float))
    t_ode_norm = _normalise(ode_result.t)

    print("\n--- Normalised-time error summary ---")
    print(f"{'Card':<12} {'RMSE':>8} {'MAE':>8} {'Max |err|':>10}")
    print("-" * 42)
    for ode_idx, card in enumerate(_ODE_CARD_ORDER):
        sim_avg = _cumulative_avg(pop_hist[card])
        ode_at_sim = _interpolate_ode_at_sim_times(
            t_ode_norm, ode_result.y[ode_idx], t_sim_norm
        )
        diff = sim_avg - ode_at_sim
        rmse = float(np.sqrt(np.mean(diff ** 2)))
        mae = float(np.mean(np.abs(diff)))
        max_err = float(np.max(np.abs(diff)))
        print(f"{card.name:<12} {rmse:>8.4f} {mae:>8.4f} {max_err:>10.4f}")
    print("-------------------------------------")
