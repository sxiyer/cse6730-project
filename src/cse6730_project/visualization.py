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
