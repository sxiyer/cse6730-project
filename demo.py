"""
Demo script: runs the RPS market simulation with all four scalper types.

Usage (from repo root):
    python demo.py
"""

from src.cse6730_project.simulation import Simulation
from src.cse6730_project.market.markets import MarketCommon
from src.cse6730_project.agents import NaiveGambler, Shadow, QuickGrabber, MarketMaker
from src.cse6730_project.models import Card
from src.cse6730_project.games import GameResultType
from src.cse6730_project.utils import rng_rand

NUM_PLAYERS = 4
NUM_NAIVE_GAMBLERS = 2
NUM_SHADOWS = 2
NUM_QUICK_GRABBERS = 2
NUM_MARKET_MAKERS = 2
NUM_SCALPERS = NUM_NAIVE_GAMBLERS + NUM_SHADOWS + NUM_QUICK_GRABBERS + NUM_MARKET_MAKERS
NUM_TICKS = 15
SCALPER_BUDGET = 10.0

# Set to an integer for a reproducible run, or None for a fresh random run each time.
SEED = None

rng_rand.seed(SEED)

_SCALPER_SUMMARY = (
    f"{NUM_NAIVE_GAMBLERS} NaiveGambler, "
    f"{NUM_SHADOWS} Shadow, "
    f"{NUM_QUICK_GRABBERS} QuickGrabber, "
    f"{NUM_MARKET_MAKERS} MarketMaker"
)

market = MarketCommon()
sim = Simulation(
    market=market,
    num_players=NUM_PLAYERS,
    num_scalpers=NUM_SCALPERS,
    scalper_type={
        NaiveGambler: NUM_NAIVE_GAMBLERS,
        Shadow: NUM_SHADOWS,
        QuickGrabber: NUM_QUICK_GRABBERS,
        MarketMaker: NUM_MARKET_MAKERS,
    },
    num_ticks=NUM_TICKS,
    seed=SEED,
)

for s in sim.scalpers:
    s.money = SCALPER_BUDGET


def _label(s):
    if isinstance(s, NaiveGambler):
        prefix = "NG"
    elif isinstance(s, Shadow):
        prefix = "SH"
    elif isinstance(s, QuickGrabber):
        prefix = "QG"
    else:
        prefix = "MM"
    return f"{prefix}-{str(s.UID)[-4:]}"


scalper_labels = {s.UID: _label(s) for s in sim.scalpers}

print(f"Running {NUM_TICKS} ticks | {NUM_PLAYERS} players | {NUM_SCALPERS} scalpers ({_SCALPER_SUMMARY})\n")
print(f"{'Tick':<6} {'R price':>9} {'P price':>9} {'S price':>9} {'R stock':>9} {'P stock':>9} {'S stock':>9}")
print("-" * 66)

for tick in range(NUM_TICKS):
    sim.next_tick()
    p = market.prices
    st = market.stock
    print(
        f"{tick:<6} "
        f"{p[Card.ROCK]:>9.4f} {p[Card.PAPER]:>9.4f} {p[Card.SCISSOR]:>9.4f} "
        f"{st[Card.ROCK]:>9} {st[Card.PAPER]:>9} {st[Card.SCISSOR]:>9}"
    )

print("\n=== Final scalper state ===")
print(f"{'Agent':<10}  {'money':>8}  {'ROCK':>6}  {'PAPER':>6}  {'SCISSOR':>8}")
for s in sim.scalpers:
    d = s.deck
    label = scalper_labels[s.UID]
    print(
        f"{label:<10}  {s.money:>8.2f}  "
        f"{d[Card.ROCK]:>6}  {d[Card.PAPER]:>6}  {d[Card.SCISSOR]:>8}"
    )

print("\n=== Final player win/loss record ===")
for p in sim.players:
    wins   = sum(1 for r in p.history if r == GameResultType.WIN)
    losses = sum(1 for r in p.history if r == GameResultType.LOSS)
    ties   = sum(1 for r in p.history if r == GameResultType.TIE)
    print(f"Player {str(p.UID)[-4:]}: W={wins} L={losses} T={ties}")
