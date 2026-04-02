from cards import Card
from market import Market
from order import *

class MarketCommon(Market):
    def __init__(self):
        super().__init__(name = "simple")
        self.stock = {card: 1000 for card in Card}
        self.prices = {card: 1.0 for card in Card}
    
    def submit_order(self, order):
        # BUY ORDER
        if order.order_type == OrderType.BUY:
            if order.quantity <= self.stock[order.card_type]:
                if order.limit_price <= self.prices[order.card_type]:
                    return True
                else:
                    return False # Order price too low for requested card value
            else:
                return False # Market does not have enough stock

        # SELL ORDER
        else:
            return True