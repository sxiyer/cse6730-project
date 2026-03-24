import readchar

from rich.console import Console
from rich.layout import Layout
from rich.table import Table
from rich.live import Live

from .footer import Footer
from .header import Header
from .home_screen import HomeScreen
from .leader_board import LeaderBoard
from .match_results import MatchResults


class SimulationApp:
    def __init__(self):
        self.layout = self._build_home_layout()
        self.console = Console()
        self.num_players = 0
        self.num_rounds = 0

    def run(self):
        """Run the simulation app."""
        with Live(
            self.layout, console=self.console, screen=True, transient=True
        ) as live:
            while True:
                key = readchar.readkey()
                if key.lower() == "q":
                    break
                elif key == " ":
                    self.layout = self._build_running_layout()
                    live.update(self.layout)
                    self._update(None)

    def _build_home_layout(self) -> Layout:
        """Build the initial home screen layout."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        layout["header"].update(Header())
        layout["body"].update(HomeScreen())
        layout["footer"].update(Footer())
        return layout

    def _build_running_layout(self) -> Layout:
        """Build the main simulation layout."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        layout["body"].split_row(
            Layout(name="leader_board"), Layout(name="match_results")
        )
        layout["header"].update(Header())
        layout["leader_board"].update(LeaderBoard())
        layout["match_results"].update(MatchResults())
        layout["footer"].update(Footer())
        return layout

    def _update(self, state):
        self.layout["header"].update(Header())
        self.layout["leader_board"].update(LeaderBoard())
        self.layout["match_results"].update(MatchResults())
        self.layout["footer"].update(Footer())
