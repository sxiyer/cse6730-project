from dataclasses import dataclass, field


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
