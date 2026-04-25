from dataclasses import replace

from ..models import Card, Order, OrderType
from . import Market


class MarketCommon(Market):
    def __init__(self):
        super().__init__(name="common")

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

        # TODO Fix transcation logic: it returns none!!
        if self.buy_list and self.sell_list:
            for order in self.buy_list:
                replace(order, executed=False)
            for order in self.sell_list:
                replace(order, executed=False)

        self.sell_list = None
        self.buy_list = None


class MarketSimple(Market):
    def __init__(self):
        super().__init__(name="simple")
