from dataclasses import dataclass
from pathlib import Path
import os
import numpy as np

from .models import Card, OdeConfig, TimeConfig, FitnessModes

NUM_PLAYERS = 500
NUM_SCALPERS = 2
NUM_TICKS = 500
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

RNG_SEED = 442

PLAYER_STARTING_MONEY = 10.0
SCALPER_STARTING_MONEY = 10.0

PAYOFF: dict[tuple[Card, Card], int] = {
    (Card.ROCK, Card.SCISSOR): 1,
    (Card.SCISSOR, Card.PAPER): 1,
    (Card.PAPER, Card.ROCK): 1,
}

PAYOFF_NP = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]], dtype=float)

FIT_WINDOW_SIZE = 50
FIT_MODE = FitnessModes.EXPECTED


SEED_DECK_WEIGHTS: dict[Card, float] = {
    Card.ROCK: 5,
    Card.PAPER: 2,
    Card.SCISSOR: 1,
}


# Baseline ODE solver default params.
# Used in ode.py

ODE_PARAMS = OdeConfig(
    z=1.1,
    mu=0.01,
    t_interval=TimeConfig(start=0, end=10),
    t_eval=TimeConfig(start=0, end=10, step=10),
)

ODE_SCALE = 16.0


# Visualization configs
VIZ_DIRS = ["plots/", "plots/ode", "plots/sim"]


@dataclass(frozen=True)
class VizConfig:
    base_dir: Path = Path("plots")
    img_format: str = ".png"
    img_dpi: int = 300
    show_axes: bool = True
