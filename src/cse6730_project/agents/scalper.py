from dataclasses import replace
from typing import Callable
from abc import abstractmethod
from uuid import UUID, uuid4

from ..models import Order, CardPrices, Card, OrderType, AgentType
from ..utils import rng_rand
from .base import Agent


class Scalper(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, agent_type=AgentType.SCALPER, money=money)

    def wake_up_agent(self, card_prices: CardPrices) -> tuple[list[Order], list[Order]]:
        """create a list of orders with callbacks to update agent"""
        buy_order = self._buy_order(card_prices)
        sell_order = self._sell_order(card_prices)

        return (buy_order, sell_order)

    def _create_order(self, order: Order) -> Order:

        def update_agent() -> None:
            if order and order.executed and order.order_type == OrderType.BUY:
                self.deck[order.card_type] += order.quantity
                self.money -= order.exchange_price * order.quantity
            if order and order.executed and order.order_type == OrderType.BUY:
                self.deck[order.card_type] -= order.quantity
                self.money += order.exchange_price * order.quantity

        order = replace(order, callback=update_agent)

        return order

    def _buy_order(self, card_prices: CardPrices) -> list[Order]:
        return list()

    def _sell_order(self, card_prices: CardPrices) -> list[Order]:
        return list()


class Shadow(Scalper):
    """
    EMA trend-filtered mean-reversion scalper.

    Previous versions failed because they bought dips into sustained downtrends,
    accumulating cards that kept losing value tick after tick. NaiveGambler
    survives better because its random buy-rejection temporarily exits the market
    (stays cash) during parts of the downturn.

    Key insight: only buy a "dip" when the EMA itself is flat or rising (dip within
    an uptrend = genuine buy opportunity). If the EMA is falling, the card is in a
    downtrend — hold cash instead. Also exit existing positions immediately when
    the EMA turns negative (downtrend detected after entry).

    Entry: buy the card most underpriced relative to its EMA, only when that
    card's EMA is flat or rising (trend_window-tick EMA change ≥ 0).

    Exit (priority order):
      1. Trend-reversal exit — sell any held card whose EMA is now falling.
      2. Recovery exit — sell when price returns to or above EMA.
      3. Forced exit — sell after max_hold_ticks regardless.
    """

    def __init__(
        self,
        uid: UUID,
        money: float = 0.0,
        max_hold_ticks: int = 12,
        ema_alpha: float = 0.3,
        trend_window: int = 3,
    ):
        super().__init__(uid, money)
        self.max_hold_ticks = max_hold_ticks
        self.ema_alpha = ema_alpha
        self.trend_window = trend_window
        self._ema: dict[Card, float] = {}
        self._ema_history: dict[Card, list[float]] = {card: [] for card in Card}
        # (card, tick_bought, entry_price) — entry_price set in callback (post-clearing actual)
        self._positions: list[tuple[Card, int, float]] = []
        self._current_tick: int = 0

    def _update_ema(self, card: Card, price: float) -> None:
        if card not in self._ema:
            self._ema[card] = price
        else:
            self._ema[card] = (
                self.ema_alpha * price + (1 - self.ema_alpha) * self._ema[card]
            )
        self._ema_history[card].append(self._ema[card])

    def _ema_trend(self, card: Card) -> float:
        """EMA change over trend_window ticks. Positive = uptrend, negative = downtrend."""
        history = self._ema_history[card]
        if len(history) < self.trend_window + 1:
            return 0.0
        return history[-1] - history[-1 - self.trend_window]

    def _create_order(self, order: Order) -> Order:
        """This function inserts a callback to an existing order"""

        def update_agent() -> None:
            if order and order.executed and order.order_type == OrderType.BUY:
                self.deck[order.card_type] += order.quantity
                self.money -= order.exchange_price * order.quantity
                self._positions.append(
                    (
                        order.card_type,
                        self._current_tick,
                        order.exchange_price,
                    )
                )
            if order and order.executed and order.order_type == OrderType.BUY:
                self.deck[order.card_type] -= order.quantity
                self.money += order.exchange_price * order.quantity

        order = replace(order, callback=update_agent)

        return order

    def _buy_order(self, card_prices: CardPrices) -> list[Order]:
        """Buy the most underpriced card — only when that card's EMA is flat or rising."""
        for card in Card:
            self._update_ema(card, card_prices[card])
        self._current_tick += 1

        held = {card for card, _, _ in self._positions}
        candidates = [
            (card, card_prices[card] / self._ema[card])
            for card in Card
            if card not in held
            and self._ema_trend(card) >= 0  # only buy in flat/uptrend
        ]
        if not candidates:
            return []
        card, ratio = min(candidates, key=lambda x: x[1])
        if ratio >= 1.0:
            return []  # no card is below its EMA
        orders = [
            Order(
                agent_UID=self.UID,
                order_type=OrderType.BUY,
                card_type=card,
                limit_price=card_prices[card],
                order_UID=uuid4(),
                callback=None,
                executed=None,
            )
        ]

        orders = list(map(self._create_order, orders))  # Insert the callback function

        return orders

    def _sell_order(self, card_prices: CardPrices) -> list[Order]:
        """Exit when EMA turns negative, price recovers to EMA, or at max_hold_ticks."""
        for i, (card, tick_bought, _) in enumerate(self._positions):
            if self.deck[card] <= 0:
                continue
            ratio = card_prices[card] / self._ema.get(card, card_prices[card])
            trend = self._ema_trend(card)
            # Priority 1: trend-reversal — EMA started falling after we bought, cut losses
            if trend < 0:
                self._positions.pop(i)
                orders = [
                    Order(
                        agent_UID=self.UID,
                        order_type=OrderType.SELL,
                        card_type=card,
                        limit_price=card_prices[card],
                        order_UID=uuid4(),
                        callback=None,
                        executed=None,
                    )
                ]

                orders = list(
                    map(self._create_order, orders)
                )  # Insert the callback function

                # Insert the callback function
                return orders
            # Priority 2: price recovered to or above EMA
            if ratio >= 1.0:
                self._positions.pop(i)
                orders = [
                    Order(
                        agent_UID=self.UID,
                        order_type=OrderType.SELL,
                        card_type=card,
                        limit_price=card_prices[card],
                        order_UID=uuid4(),
                        callback=None,
                        executed=None,
                    )
                ]

                orders = list(
                    map(self._create_order, orders)
                )  # Insert the callback function

                return orders

        # Priority 3: forced exit
        for i, (card, tick_bought, _) in enumerate(self._positions):
            if (
                self._current_tick - tick_bought >= self.max_hold_ticks
                and self.deck[card] > 0
            ):
                self._positions.pop(i)
                orders = [
                    Order(
                        agent_UID=self.UID,
                        order_type=OrderType.SELL,
                        card_type=card,
                        limit_price=card_prices[card],
                        order_UID=uuid4(),
                        callback=None,
                        executed=None,
                    )
                ]

                orders = list(
                    map(self._create_order, orders)
                )  # Insert the callback function

                return orders

        return []


class NaiveGambler(Scalper):
    """
    Baseline scalper. Buys and sells cards randomly with no regard for price or demand.
    Each tick it submits one random buy order and one random sell order (if it owns any cards).
    """

    def _buy_order(self, card_prices: CardPrices) -> list[Order]:
        card = rng_rand.choice(list(Card))
        price = round(rng_rand.uniform(0.5, 2.0), 2)
        # TODO: What if the market could tell the agent the buy/sell spread?
        orders = [
            Order(
                agent_UID=self.UID,
                order_type=OrderType.BUY,
                card_type=card,
                limit_price=price,
                order_UID=uuid4(),
                callback=None,
                executed=None,
            )
        ]
        orders = list(map(self._create_order, orders))  # Insert the callback function
        return orders

    def _sell_order(self, card_prices: CardPrices) -> list[Order]:
        owned = [card for card, count in self.deck.items() if count > 0]
        if not owned:
            return []
        card = rng_rand.choice(owned)
        price = round(rng_rand.uniform(0.5, 2.0), 2)
        orders = [
            Order(
                agent_UID=self.UID,
                order_type=OrderType.SELL,
                card_type=card,
                limit_price=price,
                order_UID=uuid4(),
                callback=None,
                executed=None,
            )
        ]
        orders = list(map(self._create_order, orders))  # Insert the callback function
        return orders
