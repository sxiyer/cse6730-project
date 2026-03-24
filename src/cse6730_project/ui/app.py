import readchar

from rich.console import Console
from rich.layout import Layout
from rich.table import Table
from rich.live import Live

from .footer import Footer
from .header import Header
from .leader_board import LeaderBoard
from .match_results import MatchResults


class SimulationApp:
    def __init__(self):
        self.layout = self._build_layout()
        self.console = Console()

    def run(self):
        with Live(
            self.layout,
            console=self.console,
            screen=True,
            transient=True,
            refresh_per_second=4,
        ):
            while True:
                key = readchar.readkey()
                if key.lower() == "q":
                    break
                elif key == " ":
                    self._update(None)

    def _build_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        layout["body"].split_row(
            Layout(name="leader_board"), Layout(name="match_results")
        )
        self.layout["header"].update(Header())
        self.layout["leader_board"].update(LeaderBoard())
        self.layout["match_results"].update(MatchResults())
        self.layout["footer"].update(Footer())
        return layout

    def _update(self, state):
        self.layout["header"].update(Header())
        self.layout["leader_board"].update(LeaderBoard())
        self.layout["match_results"].update(MatchResults())
        self.layout["footer"].update(Footer())
