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
            self._ema[card] = self.ema_alpha * price + (1 - self.ema_alpha) * self._ema[card]
        self._ema_history[card].append(self._ema[card])

    def _ema_trend(self, card: Card) -> float:
        """EMA change over trend_window ticks. Positive = uptrend, negative = downtrend."""
        history = self._ema_history[card]
        if len(history) < self.trend_window + 1:
            return 0.0
        return history[-1] - history[-1 - self.trend_window]

    def wake_up_agent(self, card_prices: CardPrices):
        """Override to record entry prices from actual post-clearing prices paid."""
        buy_order = self.buy_order(card_prices)
        sell_order = self.sell_order(card_prices)

        def update_agent(successful: bool, exchanged_prices) -> None:
            if successful and buy_order:
                self.deck[buy_order.card_type] += buy_order.quantity
                self.money -= exchanged_prices[buy_order.card_type] * buy_order.quantity
                self._positions.append((
                    buy_order.card_type,
                    self._current_tick,
                    exchanged_prices[buy_order.card_type],
                ))
            if successful and sell_order:
                self.deck[sell_order.card_type] -= sell_order.quantity
                self.money += exchanged_prices[sell_order.card_type] * sell_order.quantity

        return (buy_order, sell_order, update_agent)

    def buy_order(self, card_prices: CardPrices) -> Order | None:
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
            return None
        card, ratio = min(candidates, key=lambda x: x[1])
        if ratio >= 1.0:
            return None  # no card is below its EMA
        return Order(
            agent_UID=self.UID,
            order_type=OrderType.BUY,
            card_type=card,
            limit_price=card_prices[card],
        )

    def sell_order(self, card_prices: CardPrices) -> Order | None:
        """Exit when EMA turns negative, price recovers to EMA, or at max_hold_ticks."""
        for i, (card, tick_bought, _) in enumerate(self._positions):
            if self.deck[card] <= 0:
                continue
            ratio = card_prices[card] / self._ema.get(card, card_prices[card])
            trend = self._ema_trend(card)
            # Priority 1: trend-reversal — EMA started falling after we bought, cut losses
            if trend < 0:
                self._positions.pop(i)
                return Order(
                    agent_UID=self.UID,
                    order_type=OrderType.SELL,
                    card_type=card,
                    limit_price=card_prices[card],
                )
            # Priority 2: price recovered to or above EMA
            if ratio >= 1.0:
                self._positions.pop(i)
                return Order(
                    agent_UID=self.UID,
                    order_type=OrderType.SELL,
                    card_type=card,
                    limit_price=card_prices[card],
                )

        # Priority 3: forced exit
        for i, (card, tick_bought, _) in enumerate(self._positions):
            if self._current_tick - tick_bought >= self.max_hold_ticks and self.deck[card] > 0:
                self._positions.pop(i)
                return Order(
                    agent_UID=self.UID,
                    order_type=OrderType.SELL,
                    card_type=card,
                    limit_price=card_prices[card],
                )

        return None


class QuickGrabber(Scalper):
    """
    Micro-momentum scalper.

    Entry: buy the card with the strongest price rise over the last
    momentum_window ticks, provided that rise exceeds min_momentum.

    Exit (priority order):
      1. Profit target — sell when price >= entry_price * (1 + profit_target).
      2. Stop-loss    — sell when price <= entry_price * (1 - stop_loss).
      3. Forced exit  — sell after max_hold_ticks regardless.
    """

    def __init__(
        self,
        uid: UUID,
        money: float = 0.0,
        momentum_window: int = 2,
        min_momentum: float = 0.05,
        profit_target: float = 0.04,
        stop_loss: float = 0.03,
        max_hold_ticks: int = 5,
    ):
        super().__init__(uid, money)
        self.momentum_window = momentum_window
        self.min_momentum = min_momentum
        self.profit_target = profit_target
        self.stop_loss = stop_loss
        self.max_hold_ticks = max_hold_ticks
        self._price_history: dict[Card, list[float]] = {card: [] for card in Card}
        # (card, tick_bought, entry_price) — entry_price set post-clearing in callback
        self._positions: list[tuple[Card, int, float]] = []
        self._current_tick: int = 0

    def _momentum(self, card: Card) -> float:
        """Fractional price change over momentum_window ticks."""
        h = self._price_history[card]
        if len(h) < self.momentum_window + 1:
            return 0.0
        old = h[-1 - self.momentum_window]
        return (h[-1] - old) / old

    def wake_up_agent(self, card_prices: CardPrices):
        buy_order = self.buy_order(card_prices)
        sell_order = self.sell_order(card_prices)

        def update_agent(successful: bool, exchanged_prices) -> None:
            if successful and buy_order:
                self.deck[buy_order.card_type] += buy_order.quantity
                self.money -= exchanged_prices[buy_order.card_type] * buy_order.quantity
                self._positions.append((
                    buy_order.card_type,
                    self._current_tick,
                    exchanged_prices[buy_order.card_type],
                ))
            if successful and sell_order:
                self.deck[sell_order.card_type] -= sell_order.quantity
                self.money += exchanged_prices[sell_order.card_type] * sell_order.quantity

        return (buy_order, sell_order, update_agent)

    def buy_order(self, card_prices: CardPrices) -> Order | None:
        """Buy the card with the strongest upward momentum above min_momentum."""
        for card in Card:
            self._price_history[card].append(card_prices[card])
        self._current_tick += 1

        held = {card for card, _, _ in self._positions}
        best_card: Card | None = None
        best_momentum = self.min_momentum  # floor; must strictly exceed to qualify

        for card in Card:
            if card in held:
                continue
            m = self._momentum(card)
            if m > best_momentum:
                best_momentum = m
                best_card = card

        if best_card is None:
            return None
        return Order(
            agent_UID=self.UID,
            order_type=OrderType.BUY,
            card_type=best_card,
            limit_price=card_prices[best_card],
        )

    def sell_order(self, card_prices: CardPrices) -> Order | None:
        """Exit at profit target, stop-loss, or max_hold_ticks."""
        for i, (card, _, entry_price) in enumerate(self._positions):
            if self.deck[card] <= 0:
                continue
            current = card_prices[card]
            if current >= entry_price * (1 + self.profit_target):
                self._positions.pop(i)
                return Order(
                    agent_UID=self.UID,
                    order_type=OrderType.SELL,
                    card_type=card,
                    limit_price=current,
                )
            if current <= entry_price * (1 - self.stop_loss):
                self._positions.pop(i)
                return Order(
                    agent_UID=self.UID,
                    order_type=OrderType.SELL,
                    card_type=card,
                    limit_price=current,
                )

        # Forced exit
        for i, (card, tick_bought, _) in enumerate(self._positions):
            if self._current_tick - tick_bought >= self.max_hold_ticks and self.deck[card] > 0:
                self._positions.pop(i)
                return Order(
                    agent_UID=self.UID,
                    order_type=OrderType.SELL,
                    card_type=card,
                    limit_price=card_prices[card],
                )

        return None


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
