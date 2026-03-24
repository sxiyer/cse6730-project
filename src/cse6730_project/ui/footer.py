from rich.text import Text
from rich.panel import Panel


class Footer:
    def __init__(self):
        pass

    def __rich__(self) -> Panel:
        text = Text(justify="center")
        text.append("[dim][SPACE][/] next round    [dim][Q][/] quit & save")
        return Panel(text)
