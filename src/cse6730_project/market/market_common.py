from ..models import Card, Order, OrderType
from ..market import Market


class MarketCommon(Market):
    def __init__(self):
        super().__init__(name="common")
        self.stock = {card: 1000 for card in Card}
        self.prices = {card: 1.0 for card in Card}
        self.buy_list: list[Order] = []
        self.sell_list: list[Order] = []
        self.executed_trades: list[Order] = []

    def submit_order(self, order: Order) -> bool:
        if order.order_type == OrderType.BUY:
            # Accept buy if agent is willing to pay at least the current price
            # and the market has enough stock
            if order.quantity <= self.stock[order.card_type] and \
               order.limit_price >= self.prices[order.card_type]:
                self.buy_list.append(order)
                return True
            return False
        else:  # SELL
            self.sell_list.append(order)
            return True

    def clear(self) -> None:
        """
        Process all queued orders per card type.
        - Execute accepted buys: deduct stock, record trade.
        - Execute all sells: add to stock, record trade.
        - Update price based on net demand: +5% if more buys, -5% if more sells.
        """
        for card in Card:
            buys = [o for o in self.buy_list if o.card_type == card]
            sells = [o for o in self.sell_list if o.card_type == card]

            # Price update: simple supply/demand
            net = len(buys) - len(sells)
            if net > 0:
                self.prices[card] = round(self.prices[card] * 1.05, 4)
            elif net < 0:
                self.prices[card] = round(self.prices[card] * 0.95, 4)

            for order in buys:
                if self.stock[card] >= order.quantity:
                    self.stock[card] -= order.quantity
                    self.executed_trades.append(order)

            for order in sells:
                self.stock[card] += order.quantity
                self.executed_trades.append(order)

        self.buy_list.clear()
        self.sell_list.clear()

    def execute_trade(self) -> None:
        pass  # trade execution is handled inside clear()

    def getBalance(self) -> dict:
        return {card: self.stock[card] * self.prices[card] for card in Card}

    def shuffleOrder(self) -> None:
        import random
        random.shuffle(self.buy_list)
        random.shuffle(self.sell_list)
