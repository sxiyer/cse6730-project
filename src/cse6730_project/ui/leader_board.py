import random

from rich.table import Table
from rich import box


class LeaderBoard:
    def __init__(self):
        pass

    def __rich__(self) -> Table:
        table = Table(
            title="Leader Board",
            title_justify="center",
            expand=True,
            box=box.ASCII_DOUBLE_HEAD,
        )
        table.add_column("Player", justify="center")
        table.add_column("Score", justify="center")

        order = list(range(1, 5))
        random.shuffle(order)
        for player in order:
            table.add_row(f"Player {player}", f"{random.randint(0, 100)}")
        return table
