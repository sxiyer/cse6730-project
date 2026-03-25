import readchar

from rich.console import Console
from rich.layout import Layout
from rich.live import Live

from .states import (
    SimulationContext,
    HomePlayerState,
    AppState,
)


class SimulationApp:
    def __init__(self):
        self.state: AppState | None = HomePlayerState()
        self.context = SimulationContext()
        self.console = Console()
        self.layout = self.state.render(Layout(), self.context)

    def run(self):
        """Run the simulation app."""
        with Live(
            self.layout,
            console=self.console,
            screen=True,
            transient=True,
            refresh_per_second=10,
        ) as live:
            while self.state is not None:
                key = readchar.readkey()
                self.state = self.state.handle_input(key, self.context)
                if self.state is not None:
                    self.layout = self.state.render(self.layout, self.context)
                    live.update(self.layout)
                # simulation.step()
