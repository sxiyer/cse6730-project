import os
from datetime import datetime
from typing import TYPE_CHECKING
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

from .utils import logger
from .config import VIZ_DIRS, VizConfig, ODE_PARAMS, ODE_SCALE
from .models import Card

if TYPE_CHECKING:
    from .simulation.simulation import Simulation


class Visualizer:
    def __init__(self):
        self.base_dir = VizConfig.base_dir
        self.img_format = VizConfig.img_format
        self.img_dpi = VizConfig.img_dpi
        self.show_axes = VizConfig.show_axes

        for d in VIZ_DIRS:
            d = Path(d)
            if not Path.exists(d):
                os.mkdir(d)

    def save_fig(self):
        pass


class ODEVisualizer(Visualizer):
    def save_fig_ode(
        self, t: list[float], ys: list[list[float]], simparams: dict | None
    ):
        # TODO : Pass sim params into ODEViz so that we can label which line
        # corresponds to R,P,S
        fig, ax = plt.subplots(figsize=(5, 3))

        for i, y in enumerate(ys):
            # logger.debug(f"y{i} : {y}")
            ax.plot(t, y, linewidth=1.5)

        if simparams is None:
            fname = datetime.now().strftime("%Y%m%d_%H%M%S_%d")
        else:
            fname = "oops"

        title_string = f"mu = {ODE_PARAMS.mu}, z = {ODE_PARAMS.z}"

        ax.legend(
            [
                "Rock",
                "Paper",
                "Scissors",
            ],
            fontsize="large",
            title=title_string,
        )
        ax.axhline(y=0, color="black", linestyle="--")
        ax.axvline(color="grey")
        ax.set_xlabel("Steps")
        ax.set_ylabel("Population Ratio")
        ax.autoscale()
        ode_fig_dir = self.base_dir / "ode" / f"{fname}{VizConfig.img_format}"

        fig.savefig(ode_fig_dir, dpi=self.img_dpi, bbox_inches="tight")


class ComparisonVisualizer(Visualizer):
    # ODE y-rows map to cards in this order (set by OdeRPS.convert_initial_pop_to_float)
    _ODE_CARD_ORDER = [Card.ROCK, Card.SCISSOR, Card.PAPER]
    _COLORS = {
        Card.ROCK: "tab:blue",
        Card.PAPER: "tab:orange",
        Card.SCISSOR: "tab:green",
    }

    def plot_sim_vs_ode(
        self,
        sim: "Simulation",
        ode_result,
        num_players: int,
        fname: str = "comparison",
    ) -> None:
        pop_hist = sim.get_population_history()
        n_ticks = len(sim.getHistory())

        fig, (ax_ode, ax_sim) = plt.subplots(2, 1, figsize=(7, 8), sharex=False)
        fig.suptitle(f"z={ODE_PARAMS.z}, mu={ODE_PARAMS.mu}, N={num_players}")

        # ODE solution (top)
        for i, card in enumerate(self._ODE_CARD_ORDER):
            ax_ode.plot(
                ode_result.t,
                ode_result.y[i],
                color=self._COLORS[card],
                label=card.name,
            )
        ax_ode.set_xlabel("ODE time")
        ax_ode.set_ylabel("Population fraction")
        ax_ode.set_title("ODE")
        ax_ode.legend(fontsize="small", loc="upper right")

        max_ode_time = (n_ticks - 1) / num_players
        ax_ode.set_xlim(0, max_ode_time * ODE_SCALE)

        # Simulation populations (bottom)
        # x-axis in ODE time units (tick / N)
        t_sim = [tick / num_players for tick in range(n_ticks)]

        for card in Card:
            raw_data = pop_hist[card]

            # Plot the noisy raw data in the background
            ax_sim.plot(
                t_sim,
                raw_data,
                color=self._COLORS[card],
                alpha=0.25,
                label=f"{card.name} (Raw)",
            )

            # Calculate and plot the Cumulative Time Average
            cumulative_avg = np.cumsum(raw_data) / np.arange(1, n_ticks + 1)
            ax_sim.plot(
                t_sim,
                cumulative_avg,
                color=self._COLORS[card],
                linestyle="--",
                linewidth=1.5,
                label=f"{card.name} (Avg)",
            )

        # Setup Primary X-Axis (ODE Time)
        ax_sim.set_xlabel("ODE time (tick / N)")
        ax_sim.set_ylabel("Population fraction")
        ax_sim.set_title("Simulation (Raw + Time Average)")

        max_ode_time = (n_ticks - 1) / num_players
        ax_sim.set_xlim(0, max_ode_time)

        # Setup Secondary X-Axis (Raw Ticks)
        ax_sim_raw = ax_sim.twiny()
        ax_sim_raw.set_xlabel("Simulation Ticks (Raw)")
        ax_sim_raw.set_xlim(0, n_ticks - 1)

        # SYNCHRONIZE Y-AXES
        # Get the y-limits driven by the noisy simulation data
        sim_ymin, sim_ymax = ax_sim.get_ylim()

        # Apply the SIM limits to the ODE plot to ensure an apples-to-apples scale
        ax_ode.set_ylim(sim_ymin, sim_ymax)

        # Put legend outside the plot so it doesn't cover the data
        ax_sim.legend(fontsize="small", loc="upper right")

        fig.tight_layout()

        # Save plot
        save_fname = datetime.now().strftime("%Y%m%d_%H%M%S_%d")
        sim_fig_dir = self.base_dir / "sim" / f"{save_fname}{VizConfig.img_format}"

        fig.savefig(sim_fig_dir, dpi=self.img_dpi, bbox_inches="tight")
        plt.close(fig)


class ErrorVisualizer(Visualizer):
    """
    Produces three plot files per call to plot_error():

      *_sim.png      — simulation raw populations + cumulative averages
      *_error.png    — trajectory overlap (sim avg vs ODE) + signed error
      *_combined.png — all four panels in one figure (2 × 2 grid)
    """

    # Must match OdeRPS.convert_initial_pop_to_float row order
    _ODE_CARD_ORDER = [Card.ROCK, Card.SCISSOR, Card.PAPER]
    _COLORS = {
        Card.ROCK: "tab:blue",
        Card.PAPER: "tab:orange",
        Card.SCISSOR: "tab:green",
    }

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def plot_error(
        self,
        sim: "Simulation",
        ode_result,
        fname: str = "error",
    ) -> None:
        """Save three PNG files to plots/error/ for one sim+ODE pair."""
        pop_hist = sim.get_population_history()
        n_ticks = len(sim.getHistory())
        t_sim_norm = self._normalise(np.arange(n_ticks, dtype=float))
        t_ode_norm = self._normalise(ode_result.t)

        # Pre-compute per-card arrays used by multiple panels
        card_data = self._compute_card_data(
            pop_hist, ode_result, t_sim_norm, t_ode_norm, n_ticks
        )

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%d")
        base = self.base_dir / "error"

        self._save_sim_fig(t_sim_norm, card_data, base, stamp, fname)
        self._save_error_fig(t_sim_norm, card_data, base, stamp, fname)
        self._save_combined_fig(
            t_sim_norm, t_ode_norm, ode_result, card_data, base, stamp, fname
        )

    # ------------------------------------------------------------------
    # Per-figure builders
    # ------------------------------------------------------------------

    def _save_sim_fig(self, t_sim_norm, card_data, base, stamp, fname):
        fig, ax = plt.subplots(figsize=(7, 4))
        self._draw_sim_ax(ax, t_sim_norm, card_data)
        fig.tight_layout()
        out = base / f"{stamp}_{fname}_sim{VizConfig.img_format}"
        fig.savefig(out, dpi=self.img_dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info("ErrorVisualizer saved: %s", out)

    def _save_error_fig(self, t_sim_norm, card_data, base, stamp, fname):
        fig, (ax_traj, ax_err) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
        fig.suptitle(
            f"Sim vs ODE — normalised time  |  z={ODE_PARAMS.z}, mu={ODE_PARAMS.mu}",
            fontsize=11,
        )
        self._draw_trajectory_ax(ax_traj, t_sim_norm, card_data)
        self._draw_error_ax(ax_err, t_sim_norm, card_data, xlabel=True)
        fig.tight_layout()
        out = base / f"{stamp}_{fname}_error{VizConfig.img_format}"
        fig.savefig(out, dpi=self.img_dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info("ErrorVisualizer saved: %s", out)

    def _save_combined_fig(
        self, t_sim_norm, t_ode_norm, ode_result, card_data, base, stamp, fname
    ):
        fig, ((ax_sim, ax_ode), (ax_traj, ax_err)) = plt.subplots(2, 2, figsize=(14, 9))
        fig.suptitle(
            f"Error analysis — normalised time  |  z={ODE_PARAMS.z}, mu={ODE_PARAMS.mu}",
            fontsize=12,
        )
        self._draw_sim_ax(ax_sim, t_sim_norm, card_data)
        self._draw_ode_ax(ax_ode, t_ode_norm, ode_result)
        self._draw_trajectory_ax(ax_traj, t_sim_norm, card_data, xlabel=True)
        self._draw_error_ax(ax_err, t_sim_norm, card_data, xlabel=True)
        fig.tight_layout()
        out = base / f"{stamp}_{fname}_combined{VizConfig.img_format}"
        fig.savefig(out, dpi=self.img_dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info("ErrorVisualizer saved: %s", out)

    # ------------------------------------------------------------------
    # Axis drawers  (reused across figures)
    # ------------------------------------------------------------------

    def _draw_sim_ax(self, ax, t_sim_norm, card_data, xlabel=False):
        for card, d in card_data.items():
            color = self._COLORS[card]
            ax.plot(
                t_sim_norm,
                d["raw"],
                color=color,
                alpha=0.25,
                linewidth=0.8,
                label=f"{card.name} raw",
            )
            ax.plot(
                t_sim_norm,
                d["avg"],
                color=color,
                linewidth=1.4,
                linestyle="--",
                label=f"{card.name} avg",
            )
        ax.set_title("Simulation (raw + cumulative avg)")
        ax.set_ylabel("Population fraction")
        if xlabel:
            ax.set_xlabel("Normalised time  [0 → 1]")
        ax.legend(fontsize="small", loc="upper right", ncol=2)

    def _draw_ode_ax(self, ax, t_ode_norm, ode_result, xlabel=False):
        for ode_idx, card in enumerate(self._ODE_CARD_ORDER):
            ax.plot(
                t_ode_norm,
                ode_result.y[ode_idx],
                color=self._COLORS[card],
                linewidth=1.5,
                label=card.name,
            )
        ax.set_title("ODE solution")
        ax.set_ylabel("Population fraction")
        if xlabel:
            ax.set_xlabel("Normalised time  [0 → 1]")
        ax.legend(fontsize="small", loc="upper right")

    def _draw_trajectory_ax(self, ax, t_sim_norm, card_data, xlabel=False):
        for card, d in card_data.items():
            color = self._COLORS[card]
            ax.plot(
                t_sim_norm,
                d["ode_at_sim"],
                color=color,
                linewidth=0.75,
                alpha=0.5,
                label=f"{card.name} ODE",
            )
            ax.plot(
                t_sim_norm,
                d["avg"],
                color=color,
                linewidth=1.2,
                linestyle="--",
                label=f"{card.name} sim avg",
            )
        ax.set_title("Trajectory overlap (normalised time)")
        ax.set_ylabel("Population fraction")
        if xlabel:
            ax.set_xlabel("Normalised time  [0 → 1]")
        ax.legend(fontsize="small", loc="upper right", ncol=2)

    def _draw_error_ax(self, ax, t_sim_norm, card_data, xlabel=False):
        for card, d in card_data.items():
            rmse = d["rmse"]
            mae = d["mae"]
            ax.plot(
                t_sim_norm,
                d["diff"],
                color=self._COLORS[card],
                linewidth=1.2,
                label=f"{card.name}  RMSE={rmse:.4f}  MAE={mae:.4f}",
            )
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_title("Signed error  (sim avg − ODE)")
        ax.set_ylabel("Sim avg − ODE")
        if xlabel:
            ax.set_xlabel("Normalised time  [0 → 1]")
        ax.legend(fontsize="small", loc="upper right")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _compute_card_data(self, pop_hist, ode_result, t_sim_norm, t_ode_norm, n_ticks):
        """Return per-card dict of pre-computed arrays for all panel drawers."""
        result = {}
        for ode_idx, card in enumerate(self._ODE_CARD_ORDER):
            raw = np.asarray(pop_hist[card], dtype=float)
            avg = np.cumsum(raw) / np.arange(1, n_ticks + 1)
            ode_at_sim = np.interp(t_sim_norm, t_ode_norm, ode_result.y[ode_idx])
            diff = avg - ode_at_sim
            result[card] = {
                "raw": raw,
                "avg": avg,
                "ode_at_sim": ode_at_sim,
                "diff": diff,
                "rmse": float(np.sqrt(np.mean(diff**2))),
                "mae": float(np.mean(np.abs(diff))),
            }
        return result

    @staticmethod
    def _normalise(arr: np.ndarray) -> np.ndarray:
        span = arr[-1] - arr[0]
        if span == 0:
            raise ValueError("Cannot normalise a constant array.")
        return (arr - arr[0]) / span
