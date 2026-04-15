from uuid import UUID

from ..models import Card, Order, OrderType
from ..utils import rng_rand
from .scalper import Scalper


class NaiveGambler(Scalper):
    """
    Baseline scalper. Buys and sells cards randomly with no regard for price or demand.
    Each tick it submits one random buy order and one random sell order (if it owns any cards).
    """

    def wake_up_agent(self) -> None:
        self.pending_orders = []
        buy = self.buy_order()
        sell = self.sell_order()
        if buy:
            self.pending_orders.append(buy)
        if sell:
            self.pending_orders.append(sell)

    def buy_order(self) -> Order:
        card = rng_rand.choice(list(Card))
        price = round(rng_rand.uniform(0.5, 2.0), 2)
        # TODO: What if the market could tell the agent the buy/sell spread?
        return Order(
            agent_UID=self.UID,
            order_type=OrderType.BUY,
            card_type=card,
            limit_price=price,
        )

    def sell_order(self) -> Order | None:
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

    