from rich.console import Console
from rich.layout import Layout
from rich.table import Table

from .footer import Footer
from .header import Header
from .leader_board import LeaderBoard
from .match_results import MatchResults


class SimulationAPP:
    def __init__(self):
        self.layout = self._build_layout()
        self.console = Console()

    def run(self):
        pass

    def _build_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header"), Layout(name="body"), Layout(name="footer")
        )
        layout["body"].split_row(
            Layout(name="leader_board"), Layout(name="match_results")
        )
        return layout

    def _update(self, state):
        self.layout["header"].update(Header())
        self.layout["footer"].update(Footer())
