from dataclasses import dataclass
from pathlib import Path
import os

from .models import Card, OdeConfig, TimeConfig


INITIAL_SUPPLY = 1000
INITIAL_PRICE = 1.0
STARTING_BUDGET = 15.0
MAX_DECK_SIZE = 9
BEST_OF = 5
WINS_NEEDED = 3
PRICE_HISTORY_LEN = 5

ROOT: Path = Path(__file__).parent

# Rich variables
COLUMNS = 10
LINES = 10

os.environ["COLUMNS"] = str(COLUMNS)
os.environ["LINES"] = str(LINES)

RNG_SEED = 440

PLAYER_STARTING_MONEY = 10.0
SCALPER_STARTING_MONEY = 10.0

PAYOFF: dict[tuple[Card, Card], int] = {
    (Card.ROCK, Card.SCISSOR): 1,
    (Card.SCISSOR, Card.PAPER): 1,
    (Card.PAPER, Card.ROCK): 1,
}


# Baseline ODE solver default params.
# Used in ode.py

ODE_PARAMS = OdeConfig(
    z=1.1,
    mu=0.02,
    t_interval=TimeConfig(start=0, end=10),
    t_eval=TimeConfig(start=0, end=10, step=10),
)


# Visualization configs
VIZ_DIRS = ["plots/", "plots/ode"]


@dataclass(frozen=True)
class VizConfig:
    base_dir: Path = Path("plots")
    img_format: str = ".png"
    img_dpi: int = 300
    show_axes: bool = True
