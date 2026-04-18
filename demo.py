"""
Demo script: runs the RPS market simulation with NaiveGambler and Shadow scalpers.

Usage (from repo root):
    python demo.py
"""

from src.cse6730_project.simulation import Simulation
from src.cse6730_project.market.markets import MarketCommon
from src.cse6730_project.agents import NaiveGambler, Shadow
from src.cse6730_project.config import RNG_SEED
from src.cse6730_project.models import Card
from src.cse6730_project.games import GameResultType

NUM_PLAYERS = 4
NUM_SCALPERS = 4   # 2 NaiveGamblers + 2 Shadows (equal ratio)
NUM_TICKS = 15
SCALPER_BUDGET = 10.0

market = MarketCommon()
sim = Simulation(
    market=market,
    num_players=NUM_PLAYERS,
    num_scalpers=NUM_SCALPERS,
    scalper_type={NaiveGambler: 2, Shadow: 2},
    num_ticks=NUM_TICKS,
    seed=RNG_SEED,
)

# Give all scalpers a starting budget
for s in sim.scalpers:
    s.money = SCALPER_BUDGET

scalper_labels = {
    s.UID: f"{'NG' if isinstance(s, NaiveGambler) else 'SH'}-{str(s.UID)[-4:]}"
    for s in sim.scalpers
}

print(f"Running {NUM_TICKS} ticks | {NUM_PLAYERS} players | {NUM_SCALPERS} scalpers (2 NaiveGambler, 2 Shadow)\n")
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
