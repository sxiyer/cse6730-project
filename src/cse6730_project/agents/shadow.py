from uuid import UUID
from typing import TYPE_CHECKING

from ..models import Card, Order, OrderType
from ..config import PRICE_HISTORY_LEN
from .scalper import Scalper

if TYPE_CHECKING:
    from ..market.base import Market


class Shadow(Scalper):
    """
    Momentum-following scalper with a time-based forced exit.

    Entry: buy the card with the strongest upward price momentum.
    Exit (priority order):
      1. Forced exit — sell the oldest position held >= max_hold_ticks ticks,
         regardless of current momentum. Prevents indefinite accumulation.
      2. Momentum exit — sell any owned card whose price is now falling.

    Requires a market reference injected after creation: scalper.market = market
    """

    def __init__(self, uid: UUID, money: float = 0.0, max_hold_ticks: int = 3):
        super().__init__(uid, money)
        self.market: "Market | None" = None
        self.max_hold_ticks = max_hold_ticks
        self._price_history: dict[Card, list[float]] = {card: [] for card in Card}
        # Each entry is (card, tick_when_buy_order_was_placed).
        # We check deck[card] > 0 before selling to guard against unfilled orders.
        self._positions: list[tuple[Card, int]] = []
        self._current_tick: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _observe_prices(self) -> None:
        if self.market is None:
            return
        for card in Card:
            history = self._price_history[card]
            history.append(self.market.prices[card])
            if len(history) > PRICE_HISTORY_LEN:
                history.pop(0)

    def _momentum(self, card: Card) -> float:
        """1-tick price change. Positive = rising, negative = falling, 0 = no data."""
        history = self._price_history[card]
        if len(history) < 2:
            return 0.0
        return history[-1] - history[-2]

    # ------------------------------------------------------------------
    # Agent interface
    # ------------------------------------------------------------------

    def wake_up_agent(self) -> None:
        self._observe_prices()
        self._current_tick += 1
        self.pending_orders = []
        buy = self.buy_order()
        sell = self.sell_order()
        if buy:
            self.pending_orders.append(buy)
        if sell:
            self.pending_orders.append(sell)

    def buy_order(self) -> Order | None:
        """Buy the card with the strongest positive momentum."""
        if self.market is None:
            return None
        rising = [(card, self._momentum(card)) for card in Card if self._momentum(card) > 0]
        if not rising:
            return None
        card, _ = max(rising, key=lambda x: x[1])
        self._positions.append((card, self._current_tick))
        return Order(
            agent_UID=self.UID,
            order_type=OrderType.BUY,
            card_type=card,
            limit_price=self.market.prices[card],
        )

    def sell_order(self) -> Order | None:
        """
        Sell one card per tick, checking forced exits before momentum exits.
        """
        if self.market is None:
            return None

        # Priority 1: forced exit — oldest position that has hit max_hold_ticks
        for i, (card, tick_bought) in enumerate(self._positions):
            if self._current_tick - tick_bought >= self.max_hold_ticks and self.deck[card] > 0:
                self._positions.pop(i)
                return Order(
                    agent_UID=self.UID,
                    order_type=OrderType.SELL,
                    card_type=card,
                    limit_price=self.market.prices[card],
                )

        # Priority 2: momentum exit — owned card whose price is falling
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
            limit_price=self.market.prices[card],
        )
