from uuid import UUID

from ..models import Order, CardPrices, Card, OrderType
from ..utils import rng_rand
from .base import Agent


class Scalper(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)

    def buy_order(self, card_prices: CardPrices) -> Order | None:
        return None

    def sell_order(self, card_prices: CardPrices) -> Order | None:
        return None


class Shadow(Scalper):
    """
    Momentum-following scalper with a time-based forced exit.

    Entry: buy the card with the strongest upward price momentum.
    Exit (priority order):
      1. Forced exit - sell the oldest position held >= max_hold_ticks ticks,
         regardless of current momentum. Prevents indefinite accumulation.
      2. Momentum exit — sell any owned card whose price is now falling.

    """

    def __init__(self, uid: UUID, money: float = 0.0, max_hold_ticks: int = 3):
        super().__init__(uid, money)
        self.max_hold_ticks = max_hold_ticks
        self._price_history: dict[Card, list[float]] = {card: [] for card in Card}
        self._positions: list[tuple[Card, int]] = []
        self._current_tick: int = 0

    def _momentum(self, card: Card) -> float:
        """1-tick price change. Positive = rising, negative = falling, 0 = no data."""
        history = self._price_history[card]
        if len(history) < 2:
            return 0.0
        return history[-1] - history[-2]

    def buy_order(self, card_prices: CardPrices) -> Order | None:
        """Buy the card with the strongest positive momentum."""
        for card in Card:
            self._price_history[card].append(card_prices[card])
        self._current_tick += 1

        rising = [
            (card, self._momentum(card)) for card in Card if self._momentum(card) > 0
        ]
        if not rising:
            return None
        card, _ = max(rising, key=lambda x: x[1])
        self._positions.append((card, self._current_tick))
        return Order(
            agent_UID=self.UID,
            order_type=OrderType.BUY,
            card_type=card,
            limit_price=card_prices[card],
        )

    def sell_order(self, card_prices: CardPrices) -> Order | None:
        """
        Sell one card per tick, checking forced exits before momentum exits.
        """

        # Priority 1: forced exit — oldest position that has hit max_hold_ticks
        for i, (card, tick_bought) in enumerate(self._positions):
            if (
                self._current_tick - tick_bought >= self.max_hold_ticks
                and self.deck[card] > 0
            ):
                self._positions.pop(i)
                return Order(
                    agent_UID=self.UID,
                    order_type=OrderType.SELL,
                    card_type=card,
                    limit_price=card_prices[card],
                )

        falling = [
            (card, self._momentum(card))
            for card in Card
            if self._momentum(card) < 0 and self.deck[card] > 0
        ]
        if not falling:
            return None
        card, _ = min(falling, key=lambda x: x[1])  # steepest drop first
        # Remove the oldest position entry for this card
        for i, (c, _) in enumerate(self._positions):
            if c == card:
                self._positions.pop(i)
                break
        return Order(
            agent_UID=self.UID,
            order_type=OrderType.SELL,
            card_type=card,
            limit_price=card_prices[card],
        )


class NaiveGambler(Scalper):
    """
    Baseline scalper. Buys and sells cards randomly with no regard for price or demand.
    Each tick it submits one random buy order and one random sell order (if it owns any cards).
    """

    def buy_order(self, card_prices: CardPrices) -> Order | None:
        card = rng_rand.choice(list(Card))
        price = round(rng_rand.uniform(0.5, 2.0), 2)
        # TODO: What if the market could tell the agent the buy/sell spread?
        return Order(
            agent_UID=self.UID,
            order_type=OrderType.BUY,
            card_type=card,
            limit_price=price,
        )

    def sell_order(self, card_prices: CardPrices) -> Order | None:
        owned = [card for card, count in self.deck.items() if count > 0]
        if not owned:
            return None
        card = rng_rand.choice(owned)
        price = round(rng_rand.uniform(0.5, 2.0), 2)
        return Order(
            agent_UID=self.UID,
            order_type=OrderType.SELL,
            card_type=card,
            limit_price=price,
        )
