#!/usr/bin/env python3
"""Rock-Paper-Scissors Trading Card Game"""

import os
import random
import sys
from dataclasses import dataclass, field
from enum import Enum

# ── Constants ──────────────────────────────────────────────────────────────────

INITIAL_SUPPLY = 1000
INITIAL_PRICE = 1.0
STARTING_BUDGET = 15.0
MAX_DECK_SIZE = 9
BEST_OF = 5
WINS_NEEDED = 3
PRICE_HISTORY_LEN = 5


# ── Types ──────────────────────────────────────────────────────────────────────


class Card(Enum):
    ROCK = "Rock"
    PAPER = "Paper"
    SCISSORS = "Scissors"


BEATS = {
    Card.ROCK: Card.SCISSORS,
    Card.PAPER: Card.ROCK,
    Card.SCISSORS: Card.PAPER,
}

CARD_SYMBOLS = {
    Card.ROCK: "🪨",
    Card.PAPER: "📄",
    Card.SCISSORS: "✂️ ",
}


# ── ANSI helpers ───────────────────────────────────────────────────────────────


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"


CARD_COLORS = {
    Card.ROCK: C.RED,
    Card.PAPER: C.BLUE,
    Card.SCISSORS: C.YELLOW,
}


def colored(text: str, *codes: str) -> str:
    return "".join(codes) + text + C.RESET


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# ── Market ─────────────────────────────────────────────────────────────────────


@dataclass
class Market:
    supply: dict[Card, int] = field(
        default_factory=lambda: {c: INITIAL_SUPPLY for c in Card}
    )
    prices: dict[Card, float] = field(
        default_factory=lambda: {c: INITIAL_PRICE for c in Card}
    )
    win_rates: dict[Card, float] = field(default_factory=lambda: {c: 0.5 for c in Card})
    purchase_counts: dict[Card, int] = field(
        default_factory=lambda: {c: 0 for c in Card}
    )
    price_history: dict[Card, list[float]] = field(
        default_factory=lambda: {c: [INITIAL_PRICE] for c in Card}
    )
    wins_total: dict[Card, int] = field(default_factory=lambda: {c: 0 for c in Card})
    plays_total: dict[Card, int] = field(default_factory=lambda: {c: 0 for c in Card})
    round_number: int = 0

    def buy(self, card: Card, qty: int = 1) -> float:
        """Buy cards. Returns total cost. Raises ValueError if not enough supply."""
        if self.supply[card] < qty:
            raise ValueError(
                f"Not enough {card.value} in supply (have {self.supply[card]})"
            )
        cost = self.prices[card] * qty
        self.supply[card] -= qty
        self.purchase_counts[card] += qty
        return cost

    def record_result(self, winner: Card, loser: Card):
        self.wins_total[winner] += 1
        self.plays_total[winner] += 1
        self.plays_total[loser] += 1

    def update_prices(self):
        self.round_number += 1
        total_purchases = max(sum(self.purchase_counts.values()), 1)
        for card in Card:
            plays = self.plays_total[card]
            if plays > 0:
                self.win_rates[card] = self.wins_total[card] / plays
            else:
                self.win_rates[card] = 0.5

            purchase_volume = self.purchase_counts[card] / total_purchases
            demand_factor = self.win_rates[card] + purchase_volume
            supply_factor = self.supply[card] / INITIAL_SUPPLY
            supply_factor = max(supply_factor, 0.01)  # avoid division by zero
            self.prices[card] = round(
                INITIAL_PRICE * (demand_factor / supply_factor), 2
            )
            self.prices[card] = max(self.prices[card], 0.01)  # minimum price

            self.price_history[card].append(self.prices[card])
            if len(self.price_history[card]) > PRICE_HISTORY_LEN:
                self.price_history[card] = self.price_history[card][-PRICE_HISTORY_LEN:]

        # Reset per-round purchase counts
        self.purchase_counts = {c: 0 for c in Card}


# ── Display helpers ────────────────────────────────────────────────────────────


def print_header(text: str):
    width = 60
    print(colored("═" * width, C.DIM))
    print(colored(f" {text}", C.BOLD, C.CYAN))
    print(colored("═" * width, C.DIM))


def print_subheader(text: str):
    print(colored(f"\n  ── {text} ──", C.BOLD))


def display_market(market: Market, budget: float):
    print_header("MARKET")
    print(f"  Budget: {colored(f'${budget:.2f}', C.GREEN, C.BOLD)}")
    print(f"  Round:  {market.round_number + 1}\n")

    # Table header
    print(f"  {'Card':<14} {'Price':>8} {'Supply':>8} {'Win Rate':>10} {'Trend':>20}")
    print(f"  {'─' * 62}")

    for card in Card:
        color = CARD_COLORS[card]
        sym = CARD_SYMBOLS[card]
        name = colored(f"{sym} {card.value}", color, C.BOLD)
        price = colored(f"${market.prices[card]:.2f}", C.GREEN)
        supply = f"{market.supply[card]}"
        wr = f"{market.win_rates[card]:.0%}"

        # Price trend (sparkline-style)
        history = market.price_history[card]
        trend_parts = []
        for i, p in enumerate(history):
            if i == 0:
                trend_parts.append(f"${p:.2f}")
            else:
                prev = history[i - 1]
                if p > prev:
                    trend_parts.append(colored(f"${p:.2f}", C.GREEN))
                elif p < prev:
                    trend_parts.append(colored(f"${p:.2f}", C.RED))
                else:
                    trend_parts.append(f"${p:.2f}")
        trend = " → ".join(trend_parts[-3:])  # show last 3 for space

        # Pad name manually since it has ANSI codes
        print(f"  {name}{'':>2} {price:>18} {supply:>8} {wr:>10}  {trend}")

    print()


def display_deck(label: str, deck: list[Card], hide: bool = False):
    if hide:
        cards_str = " ".join(colored("  ?  ", C.DIM) for _ in deck)
        print(f"  {label}: [{cards_str}] ({len(deck)} cards)")
    else:
        cards_str = " ".join(
            colored(f" {CARD_SYMBOLS[c]}{c.value[0]} ", CARD_COLORS[c], C.BOLD)
            for c in deck
        )
        print(f"  {label}: [{cards_str}] ({len(deck)} cards)")


def display_scoreboard(player_wins: int, ai_wins: int):
    p = colored(str(player_wins), C.GREEN, C.BOLD)
    a = colored(str(ai_wins), C.RED, C.BOLD)
    print(f"\n  Score: You {p} — {a} AI  (first to {WINS_NEEDED})")


def display_stats(total_wins: int, total_losses: int, total_spent: float):
    print_subheader("PLAYER STATS")
    print(f"  Games Won:    {colored(str(total_wins), C.GREEN, C.BOLD)}")
    print(f"  Games Lost:   {colored(str(total_losses), C.RED, C.BOLD)}")
    print(f"  Total Spent:  {colored(f'${total_spent:.2f}', C.YELLOW)}")
    print()


# ── Deck building ──────────────────────────────────────────────────────────────


def player_buy_deck(market: Market, budget: float) -> tuple[list[Card], float]:
    """Interactive deck purchasing. Returns (deck, remaining_budget)."""
    deck: list[Card] = []
    spent = 0.0

    print_subheader("BUILD YOUR DECK (up to 9 cards)")
    print(
        f"  Commands: {colored('r', C.RED)}ock / {colored('p', C.BLUE)}aper / {colored('s', C.YELLOW)}cissors / {colored('d', C.MAGENTA)}one\n"
    )

    card_map = {"r": Card.ROCK, "p": Card.PAPER, "s": Card.SCISSORS}

    while len(deck) < MAX_DECK_SIZE:
        remaining = budget - spent
        display_deck("Current deck", deck)
        print(f"  Remaining budget: {colored(f'${remaining:.2f}', C.GREEN)}")

        affordable = [
            c for c in Card if market.prices[c] <= remaining and market.supply[c] > 0
        ]
        if not affordable and not deck:
            print(colored("  You can't afford any cards!", C.RED))
            return deck, budget - spent

        choice = (
            input(f"  Buy card [{len(deck) + 1}/{MAX_DECK_SIZE}]: ").strip().lower()
        )

        if choice == "d":
            if not deck:
                print(colored("  You need at least 1 card!", C.RED))
                continue
            break
        elif choice in card_map:
            card = card_map[choice]
            price = market.prices[card]
            if price > remaining:
                print(colored(f"  Can't afford {card.value} (${price:.2f})", C.RED))
                continue
            if market.supply[card] <= 0:
                print(colored(f"  {card.value} is sold out!", C.RED))
                continue
            cost = market.buy(card, 1)
            spent += cost
            deck.append(card)
            print(
                colored(
                    f"  Bought {CARD_SYMBOLS[card]} {card.value} for ${cost:.2f}",
                    C.GREEN,
                )
            )
        else:
            print(colored("  Invalid input. Use r/p/s/d.", C.DIM))

    if len(deck) == MAX_DECK_SIZE:
        print(colored("  Deck full!", C.YELLOW))

    return deck, budget - spent


def ai_buy_deck(market: Market, budget: float) -> tuple[list[Card], float]:
    """AI buys a deck based on win rates with some randomness."""
    deck: list[Card] = []
    spent = 0.0

    # Weight cards by win rate with noise
    while len(deck) < MAX_DECK_SIZE:
        remaining = budget - spent
        affordable = [
            c for c in Card if market.prices[c] <= remaining and market.supply[c] > 0
        ]
        if not affordable:
            break

        # Score = win_rate + random noise, penalize expensive cards slightly
        scores = {}
        for c in affordable:
            noise = random.uniform(-0.15, 0.15)
            price_penalty = (market.prices[c] - 1.0) * 0.1
            scores[c] = market.win_rates[c] + noise - price_penalty

        best = max(scores, key=scores.get)
        cost = market.buy(best, 1)
        spent += cost
        deck.append(best)

    return deck, budget - spent


# ── Combat ─────────────────────────────────────────────────────────────────────


def resolve(a: Card, b: Card) -> int:
    """Returns 1 if a wins, -1 if b wins, 0 for tie."""
    if a == b:
        return 0
    if BEATS[a] == b:
        return 1
    return -1


def play_match(player_deck: list[Card], ai_deck: list[Card], market: Market) -> bool:
    """Play best-of-5. Returns True if player wins."""
    p_deck = list(player_deck)
    a_deck = list(ai_deck)
    p_wins = 0
    a_wins = 0
    round_num = 0

    while p_wins < WINS_NEEDED and a_wins < WINS_NEEDED:
        round_num += 1
        print_subheader(f"ROUND {round_num}")
        display_scoreboard(p_wins, a_wins)
        print()

        # Player picks
        display_deck("Your deck", p_deck)
        print()
        card_map = {}
        for i, c in enumerate(p_deck):
            color = CARD_COLORS[c]
            print(
                f"    {colored(str(i + 1), C.BOLD)}) {CARD_SYMBOLS[c]} {colored(c.value, color)}"
            )
            card_map[str(i + 1)] = i

        while True:
            pick = input(f"\n  Play card (1-{len(p_deck)}): ").strip()
            if pick in card_map:
                p_card = p_deck.pop(card_map[pick])
                break
            print(colored("  Invalid choice.", C.RED))

        # AI picks (weighted toward countering common player patterns, but mostly random from deck)
        ai_idx = random.randint(0, len(a_deck) - 1)
        a_card = a_deck.pop(ai_idx)

        # Show clash
        p_display = colored(
            f"{CARD_SYMBOLS[p_card]} {p_card.value}", CARD_COLORS[p_card], C.BOLD
        )
        a_display = colored(
            f"{CARD_SYMBOLS[a_card]} {a_card.value}", CARD_COLORS[a_card], C.BOLD
        )
        print(
            f"\n  {colored('YOU', C.GREEN, C.BOLD)} played {p_display}  vs  {a_display} played by {colored('AI', C.RED, C.BOLD)}"
        )

        result = resolve(p_card, a_card)
        if result == 1:
            print(colored("  >>> You win this round! <<<", C.GREEN, C.BOLD))
            p_wins += 1
            market.record_result(p_card, a_card)
        elif result == -1:
            print(colored("  >>> AI wins this round! <<<", C.RED, C.BOLD))
            a_wins += 1
            market.record_result(a_card, p_card)
        else:
            print(colored("  >>> Tie! Replay round. <<<", C.YELLOW, C.BOLD))
            # Put cards back for a tie
            p_deck.append(p_card)
            a_deck.append(a_card)
            round_num -= 1

        # Check if either side ran out of cards
        if not p_deck and p_wins < WINS_NEEDED and a_wins < WINS_NEEDED:
            print(colored("\n  You ran out of cards!", C.RED))
            return False
        if not a_deck and a_wins < WINS_NEEDED and p_wins < WINS_NEEDED:
            print(colored("\n  AI ran out of cards!", C.GREEN))
            return True

        input(colored("  Press Enter to continue...", C.DIM))

    display_scoreboard(p_wins, a_wins)
    return p_wins >= WINS_NEEDED


# ── Main game loop ─────────────────────────────────────────────────────────────


def main():
    market = Market()
    budget = STARTING_BUDGET
    total_wins = 0
    total_losses = 0
    total_spent = 0.0

    clear_screen()
    print()
    print(
        colored(
            "  ╔══════════════════════════════════════════════════╗", C.CYAN, C.BOLD
        )
    )
    print(
        colored("  ║     ROCK  PAPER  SCISSORS  TRADING CARD GAME    ║", C.CYAN, C.BOLD)
    )
    print(
        colored(
            "  ╚══════════════════════════════════════════════════╝", C.CYAN, C.BOLD
        )
    )
    print()
    print(f"  You have {colored(f'${budget:.2f}', C.GREEN, C.BOLD)} to spend on cards.")
    print(f"  Build a deck, then battle the AI in best-of-{BEST_OF}!")
    print(f"  Card prices change based on supply and demand.\n")
    input(colored("  Press Enter to start...", C.DIM))

    while True:
        clear_screen()

        # Show stats & market
        display_stats(total_wins, total_losses, total_spent)
        display_market(market, budget)

        # Check if player can afford anything
        cheapest = min(market.prices[c] for c in Card if market.supply[c] > 0)
        if budget < cheapest:
            print(
                colored("  You can't afford any more cards. Game over!", C.RED, C.BOLD)
            )
            print(f"\n  Final record: {total_wins}W - {total_losses}L")
            print(f"  Total spent: ${total_spent:.2f}")
            break

        # Player builds deck
        player_deck, budget = player_buy_deck(market, budget)
        deck_cost = sum(market.prices.get(c, INITIAL_PRICE) for c in player_deck)
        # Actual spend was tracked in buy; recalc from budget delta is cleaner
        pre_budget = budget

        clear_screen()
        print_subheader("AI IS BUILDING A DECK...")

        # AI builds deck with same budget as player spent (keeps it fair)
        ai_budget = len(player_deck) * 1.5  # give AI a reasonable budget
        ai_deck, _ = ai_buy_deck(market, ai_budget)

        display_deck("Your deck ", player_deck)
        display_deck("AI's deck ", ai_deck, hide=True)
        print(f"\n  AI bought {len(ai_deck)} cards.")
        input(colored("\n  Press Enter to begin the match...", C.DIM))

        # Play match
        clear_screen()
        print_header("MATCH START")
        player_won = play_match(player_deck, ai_deck, market)

        print()
        if player_won:
            total_wins += 1
            print(colored("  ★★★ YOU WIN THE MATCH! ★★★", C.GREEN, C.BOLD))
            # Refund a small amount for winning
            refund = 2.0
            budget += refund
            print(colored(f"  Victory bonus: +${refund:.2f}", C.GREEN))
        else:
            total_losses += 1
            print(colored("  ✗✗✗ AI WINS THE MATCH ✗✗✗", C.RED, C.BOLD))

        # Update market
        market.update_prices()

        # Track spending (approximate from budget changes)
        spent_this_round = (
            STARTING_BUDGET - budget if total_wins + total_losses == 1 else 0
        )
        total_spent = (
            STARTING_BUDGET - budget + (total_wins * 2.0)
        )  # account for refunds

        print()
        display_market(market, budget)
        print(f"  Prices have been updated based on results!\n")

        # Continue?
        again = input("  Play again? (y/n): ").strip().lower()
        if again != "y":
            clear_screen()
            print()
            print_header("FINAL RESULTS")
            display_stats(total_wins, total_losses, total_spent)
            print("  Thanks for playing!\n")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(colored("\n\n  Goodbye!\n", C.DIM))
        sys.exit(0)
