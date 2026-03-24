from rich.table import Table
from rich.panel import Panel


class HomeScreen:
    def __init__(self, num_players: int = 2, num_rounds: int = 1):
        self.num_players = num_players
        self.num_rounds = num_rounds

    def __rich__(self) -> Panel:
        table = Table(title="R.P.S. Simulation", title_justify="center")
        table.add_column("Parameters", justify="center")
        table.add_column("Value", justify="center")
        table.add_row("Number of Players", str(self.num_players))
        table.add_row("Number of Rounds", str(self.num_rounds))
        return Panel(table)
