import os
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path

from .config import VIZ_DIRS, VizConfig


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
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axhline(y=0, color="black", linestyle="--")
        ax.axvline(color="grey")

        for y in ys:
            ax.plot(t, y, linewidth=2)

        if simparams is None:
            fname = datetime.now().strftime("%Y%m%d_%H%M%S_%d")
        else:
            fname = "oops"

        ode_fig_dir = self.base_dir / "ode" / f"{fname}{VizConfig.img_format}"

        fig.savefig(ode_fig_dir, dpi=self.img_dpi, bbox_inches="tight")
