from ..models import Card, Order, OrderType, Transaction
from . import Market


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

    def clear(self) -> list[Transaction]:
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
        return []  # TODO Implement order execution logic



class MarketSimple(Market):
    def __init__(self):
        super().__init__(name="simple")
        self.stock = {card: 1000 for card in Card}
        self.prices = {card: 1.0 for card in Card}

    def submit_order(self, order) -> bool:
        # Any order is successful
        return True
