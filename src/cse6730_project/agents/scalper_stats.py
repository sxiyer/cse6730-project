"""
Scalper stats: runs the RPS market simulation 20 times and reports
average final money per scalper type with pairwise comparisons.

Usage (from repo root):
    python -m src.cse6730_project.agents.scalper_stats
"""

from itertools import combinations
from statistics import mean

from ..simulation import Simulation
from ..market.markets import MarketCommon
from ..models import Card
from .scalper import NaiveGambler, Shadow, QuickGrabber, MarketMaker

# ── Configuration ──────────────────────────────────────────────────
NUM_RUNS = 20
NUM_PLAYERS = 4
NUM_NAIVE_GAMBLERS = 2
NUM_SHADOWS = 2
NUM_QUICK_GRABBERS = 2
NUM_MARKET_MAKERS = 2
NUM_SCALPERS = NUM_NAIVE_GAMBLERS + NUM_SHADOWS + NUM_QUICK_GRABBERS + NUM_MARKET_MAKERS
NUM_TICKS = 15
SCALPER_BUDGET = 10.0

SCALPER_TYPE_MAP = {
    NaiveGambler: NUM_NAIVE_GAMBLERS,
    Shadow: NUM_SHADOWS,
    QuickGrabber: NUM_QUICK_GRABBERS,
    MarketMaker: NUM_MARKET_MAKERS,
}

LABEL_MAP = {
    NaiveGambler: "NaiveGambler",
    Shadow: "Shadow",
    QuickGrabber: "QuickGrabber",
    MarketMaker: "MarketMaker",
}


def _scalper_type(s):
    """Return the concrete scalper class for an agent instance."""
    for cls in (NaiveGambler, Shadow, QuickGrabber, MarketMaker):
        if type(s) is cls:
            return cls
    return type(s)


def run_once(seed: int) -> dict[type, list[float]]:
    """Run a single simulation and return final money grouped by scalper type."""
    market = MarketCommon()
    sim = Simulation(
        market=market,
        num_players=NUM_PLAYERS,
        num_scalpers=NUM_SCALPERS,
        scalper_type=SCALPER_TYPE_MAP,
        num_ticks=NUM_TICKS,
        seed=seed,
    )
    # Set starting budget (matches demo.py)
    for s in sim.scalpers:
        s.money = SCALPER_BUDGET

    # Run all ticks
    for _ in range(NUM_TICKS):
        sim.next_tick()

    # Collect final money by type
    results: dict[type, list[float]] = {}
    for s in sim.scalpers:
        cls = _scalper_type(s)
        results.setdefault(cls, []).append(s.money)
    return results


def main():
    # ── Run simulations ────────────────────────────────────────────
    all_money: dict[type, list[float]] = {}
    for run_idx in range(NUM_RUNS):
        seed = 1000 + run_idx  # deterministic but varied seeds
        run_results = run_once(seed)
        for cls, monies in run_results.items():
            all_money.setdefault(cls, []).extend(monies)

    # ── Compute averages ───────────────────────────────────────────
    averages: dict[str, float] = {}
    print(f"{'Agent Type':<16} {'Avg Money':>10}  {'Samples':>8}")
    print("-" * 38)
    for cls in (NaiveGambler, Shadow, QuickGrabber, MarketMaker):
        monies = all_money.get(cls, [])
        avg = mean(monies) if monies else 0.0
        label = LABEL_MAP[cls]
        averages[label] = avg
        print(f"{label:<16} {avg:>10.4f}  {len(monies):>8}")

    # ── Pairwise comparisons ───────────────────────────────────────
    labels = list(averages.keys())
    print(f"\n{'Comparison':<35} {'Diff ($)':>10}  {'Winner'}")
    print("-" * 60)
    for a, b in combinations(labels, 2):
        diff = averages[a] - averages[b]
        winner = a if diff > 0 else (b if diff < 0 else "TIE")
        abs_diff = abs(diff)
        print(f"{a} vs {b:<20} {abs_diff:>+10.4f}  {winner}")


if __name__ == "__main__":
    main()
