from __future__ import annotations
from abc import ABC, abstractmethod

import random


from rich.table import Table
from rich import box
from rich.text import Text
from rich.panel import Panel


@abstractmethod
class BasicLayout(ABC):
    @abstractmethod
    def __rich__(self) -> Panel | Table:
        pass


class Header(BasicLayout):
    def __init__(self):
        pass

    def __rich__(self) -> Panel:
        text = Text(justify="center")
        text.append("R.P.S. Simulation")
        return Panel(text)


class Footer(BasicLayout):
    def __init__(self):
        pass

    def __rich__(self) -> Panel:
        text = Text(justify="center")
        text.append("[SPACE] next round --- [Q] quit & save")
        return Panel(text)


class MatchResults(BasicLayout):
    def __init__(self):

        pass

    def __rich__(self) -> Table:
        table = Table(
            title="Match Results",
            title_justify="center",
            expand=True,
            box=box.ASCII_DOUBLE_HEAD,
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


class HomeScreen(BasicLayout):
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


class LeaderBoard(BasicLayout):
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
