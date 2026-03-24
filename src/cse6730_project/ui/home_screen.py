from rich.table import Table
from rich.panel import Panel


class HomeScreen:
    def __init__(self):
        pass

    def __rich__(self) -> Panel:
        table = Table(title="Welcome to the CSE6730 Simulation!")
        table.add_column("Instructions", justify="center")
        table.add_row("Press [SPACE] to start the simulation.")
        table.add_row("Press [Q] to quit and save the simulation.")
        return Panel(table)
