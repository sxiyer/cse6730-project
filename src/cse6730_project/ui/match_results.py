import random

from rich.table import Table


class MatchResults:
    def __init__(self):

        pass

    def __rich__(self) -> Table:
        table = Table(
            title="Match Results",
            title_justify="center",
        )
        table.add_column("Players", justify="center")
        table.add_column("Winner", justify="center")

        # TODO: add actual match results here
        for round in range(1, 10):
            player1 = f"Player {random.randint(1, 4)}"
            player2 = f"Player {random.randint(1, 4)}"
            winner = random.choice([player1, player2])
            table.add_row(f"{player1} vs {player2}", winner)
        return table
