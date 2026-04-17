from ..models import Card, Order, OrderType, Transaction
from ..market import Market


class MarketCommon(Market):
    def __init__(self):
        super().__init__(name="common")
        self.stock = {card: 1000 for card in Card}
        self.prices = {card: 1.0 for card in Card}

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

    def clear(self) -> None:
        """
        Process all queued orders per card type.
        - Execute accepted buys: deduct stock, record trade.
        - Execute all sells: add to stock, record trade.
        - Update price based on net demand: +5% if more buys, -5% if more sells.
        """
        # TODO: This clearing function does not appear to to call back to the
        # agents who placed the order, so they actually dont know if they can
        # increase/decrease their card quantities. Implement callbacks to agents
        # so that they know if their order went through.
        # Callback format :
        # (1,0,-1) corresponds to (+1 rock, paper stays the same, -1 scissors)

        # Also: The clearing function needs to ensure that players can always
        # buy or sell such that they have 9 card decks. There should always be
        # liquidity in the market. Perhaps the scalpers are forced to always put
        # up some price for their cards such that it creates liquidity?

        # Also check if bid/ask prices are actually valid according to the
        # current values of cards. The market should match bids to asks

        for card in Card:
            if self.buy_list:
                buys = [o for o in self.buy_list if o.card_type == card]
            else:
                buys = []
            if self.sell_list:
                sells = [o for o in self.sell_list if o.card_type == card]
            else:
                sells = []

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

        if self.buy_list:
            self.buy_list.clear()
        if self.sell_list:
            self.sell_list.clear()

    def getBalance(self) -> dict:
        return {card: self.stock[card] * self.prices[card] for card in Card}

    def shuffleOrder(self) -> None:
        import random

        if self.buy_list:
            random.shuffle(self.buy_list)
        if self.sell_list:
            random.shuffle(self.sell_list)
