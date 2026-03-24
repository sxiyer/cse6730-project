import os
from pathlib import Path


INITIAL_SUPPLY = 1000
INITIAL_PRICE = 1.0
STARTING_BUDGET = 15.0
MAX_DECK_SIZE = 9
BEST_OF = 5
WINS_NEEDED = 3
PRICE_HISTORY_LEN = 5

ROOT = Path(__file__).parent

# Rich variables
COLUMNS = 10
LINES = 10

os.environ["COLUMNS"] = str(COLUMNS)
os.environ["LINES"] = str(LINES)
