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
