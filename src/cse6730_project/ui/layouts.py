from abc import ABC, abstractmethod
import random

from rich.table import Table
from rich import box
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

PRIMARY = "bright_cyan"
ACCENT = "bright_magenta"
GOLD = "bright_yellow"
DIM = "grey62"
WIN_COLOR = "bright_green"
LOSE_COLOR = "red"
BORDER = "cyan"


class BasicLayout(ABC):
    @abstractmethod
    def __rich__(self) -> Panel | Table:
        """Render the layout as a Rich Panel or Table."""
        pass


class Header(BasicLayout):
    def __rich__(self) -> Panel:
        text = Text(justify="center")
        text.append("📈 ", style=LOSE_COLOR)
        text.append("R", style=f"bold {PRIMARY}")
        text.append(".", style=DIM)
        text.append("P", style=f"bold {ACCENT}")
        text.append(".", style=DIM)
        text.append("S", style=f"bold {GOLD}")
        text.append("  S I M U L A T I O N", style=f"bold {DIM}")
        text.append("  📉 ", style=WIN_COLOR)
        return Panel(
            Align.center(text),
            border_style=BORDER,
            box=box.HEAVY,
        )


class Footer(BasicLayout):
    def __rich__(self) -> Panel:
        text = Text(justify="center")
        text.append("  SPACE ", style=f"bold black on {PRIMARY}")
        text.append(" next round", style=DIM)
        text.append("    ·    ", style=DIM)
        text.append("  Q ", style=f"bold black on {ACCENT}")
        text.append(" quit & save  ", style=DIM)
        return Panel(
            Align.center(text),
            border_style=BORDER,
            box=box.HEAVY,
        )


class HomeScreen(BasicLayout):

    def __init__(self, num_players: int = 2, num_rounds: int = 1):
        self.num_players = num_players
        self.num_rounds = num_rounds

    def __rich__(self) -> Panel:
        table = Table(
            title="R.P.S. Simulation",
            title_justify="center",
            expand=True,
            box=box.ASCII_DOUBLE_HEAD,
            header_style=f"bold {PRIMARY}",
            border_style=DIM,
        )
        table.add_column("PARAMETER", justify="left", style=DIM, min_width=20)
        table.add_column("VALUE", justify="right", style=f"bold {GOLD}", min_width=10)
        table.add_row("🤖 NUMBER OF PLAYERS", str(self.num_players))
        table.add_row("🪜 STEP SIZE", str(self.num_rounds))
        return Panel(table)


class MatchResults(BasicLayout):
    def __rich__(self) -> Panel:
        table = Table(
            box=box.SIMPLE_HEAVY,
            expand=True,
            show_header=True,
            header_style=f"bold {PRIMARY}",
            border_style=DIM,
        )
        table.add_column("MATCHUP", justify="center", style=DIM)
        table.add_column("WINNER", justify="center")

        moves = {"✊": LOSE_COLOR, "✋": WIN_COLOR, "✌️": GOLD}

        # TODO: replace with actual match results
        for _ in range(1, 10):
            p1 = f"Player {random.randint(1, 4)}"
            p2 = f"Player {random.randint(1, 4)}"
            winner = random.choice([p1, p2])
            move = random.choice(list(moves.keys()))
            color = moves[move]
            winner_text = Text()
            winner_text.append(f"{move} {winner}", style=f"bold {color}")
            table.add_row(f"{p1} vs {p2}", winner_text)

        return Panel(
            table,
            title=f"[bold {PRIMARY}]⚔  MATCH RESULTS[/]",
            border_style=PRIMARY,
            box=box.HEAVY,
        )


class LeaderBoard(BasicLayout):
    MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
    SCORE_STYLES = [
        f"bold {GOLD}",
        f"bold {DIM}",
        f"bold {LOSE_COLOR}",
    ]

    def __rich__(self) -> Panel:
        table = Table(
            box=box.SIMPLE_HEAVY,
            expand=True,
            show_header=True,
            header_style=f"bold {ACCENT}",
            border_style=DIM,
        )
        table.add_column("#", justify="center", width=4)
        table.add_column("PLAYER", justify="left", style=f"bold {PRIMARY}")
        table.add_column("SCORE", justify="right")

        # TODO: replace with actual player scores
        order = list(range(1, 5))
        random.shuffle(order)
        scores = sorted(
            [(f"Player {p}", random.randint(0, 100)) for p in order],
            key=lambda x: x[1],
            reverse=True,
        )

        for rank, (player, score) in enumerate(scores, start=1):
            medal = self.MEDALS.get(rank, f" {rank} ")
            score_style = self.SCORE_STYLES[rank - 1] if rank <= 3 else DIM
            score_text = Text(f"{score:>3}", style=score_style)
            table.add_row(str(medal), player, score_text)

        return Panel(
            table,
            title=f"[bold {ACCENT}]👑 LEADERBOARD[/]",
            border_style=ACCENT,
            box=box.HEAVY,
        )
