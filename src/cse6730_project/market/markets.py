from ..models import Card, CardPrices, Order, OrderType, Transaction
from . import Market


class MarketCommon(Market):
    def __init__(self):
        super().__init__(name="common")
        self.stock = {card: 1000 for card in Card}
        self.prices = {card: 1.0 for card in Card}

    def get_prices(self) -> CardPrices:
        return CardPrices(
            ROCK=self.prices[Card.ROCK],
            PAPER=self.prices[Card.PAPER],
            SCISSOR=self.prices[Card.SCISSOR],
        )

    def submit_order(self, order: Order) -> bool:
        if order.order_type == OrderType.BUY:
            # Accept buy if agent is willing to pay at least the current price
            # and the market has enough stock
            if (
                order.quantity <= self.stock[order.card_type]
                and order.limit_price >= self.prices[order.card_type]
            ):
                if self.buy_list:
                    self.buy_list.append(order)
                return True
            return False
        else:  # SELL
            if self.sell_list:
                self.sell_list.append(order)
            return True

    def clear(self) -> list[Transaction]:
        """
        Process all queued orders per card type.
        - Execute accepted buys: deduct stock, record trade.
        - Execute all sells: add to stock, record trade.
        - Update price based on net demand: +5% if more buys, -5% if more sells.
        Returns one Transaction per agent (deduped), so callbacks are called once.
        TODO: Check this out, may not be correct
        """
        transactions: list[Transaction] = []
        seen_agents: set = set()
        buy_volume: dict[Card, int] = {card: 0 for card in Card}
        sell_volume: dict[Card, int] = {card: 0 for card in Card}

        for order in self.buy_list or []:
            if (
                order.limit_price >= self.prices[order.card_type]
                and self.stock[order.card_type] >= order.quantity
            ):
                self.stock[order.card_type] -= order.quantity
                buy_volume[order.card_type] += order.quantity
                if order.agent_UID not in seen_agents:
                    seen_agents.add(order.agent_UID)
                    transactions.append(Transaction(agent_UID=order.agent_UID, successful=True))

        for order in self.sell_list or []:
            self.stock[order.card_type] += order.quantity
            sell_volume[order.card_type] += order.quantity
            if order.agent_UID not in seen_agents:
                seen_agents.add(order.agent_UID)
                transactions.append(Transaction(agent_UID=order.agent_UID, successful=True))

        for card in Card:
            if buy_volume[card] > sell_volume[card]:
                self.prices[card] *= 1.05
            elif sell_volume[card] > buy_volume[card]:
                self.prices[card] *= 0.95

        self.buy_list = []
        self.sell_list = []

        return transactions


class MarketSimple(Market):
    def __init__(self):
        super().__init__(name="simple")
        self.stock = {card: 1000 for card in Card}
        self.prices = {card: 1.0 for card in Card}

    def submit_order(self, order) -> bool:
        # Any order is successful
        return True
