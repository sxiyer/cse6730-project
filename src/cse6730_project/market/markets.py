from dataclasses import replace
from uuid import UUID
import bisect

from ..models import Card, Order, OrderType, AgentType
from . import Market


class MarketCommon(Market):
    def __init__(self):
        super().__init__(name="common")

    def clear(self) -> None:
        """ """
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

        """ If there are no sell or buy orders, clear both"""
        if not self.buy_list or not self.sell_list:
            if self.buy_list:
                for order in self.buy_list:
                    replace(order, executed=False)
            if self.sell_list:
                for order in self.sell_list:
                    replace(order, executed=False)
            self.buy_list = None
            self.sell_list = None
            return

        """
        Embed the orders into a graph

        - Agents are nodes
        - Orders are edges:
            - Sell orders are an in edge
            - Buy orders are an out edge

        """

        ## Count the number of buy/sell orders
        num_buy: int = 0
        num_sell: int = 0
        if self.buy_list and self.sell_list:
            num_buy = len(self.buy_list)
            num_sell = len(self.sell_list)

        visited: set = set()
        recStack: list[bool] = [False] * (num_buy + num_sell)

        ## Create Mapping for Card types:
        buy_orders_by_card: dict[Card, list[Order]] = {}
        sell_orders_by_card: dict[Card, list[Order]] = {}
        if self.buy_list and self.sell_list:
            for order in self.buy_list:
                if order.card_type not in buy_orders_by_card:
                    buy_orders_by_card[order.card_type] = [order]
                else:
                    buy_orders_by_card[order.card_type].append(order)
            for order in self.sell_list:
                if order.card_type not in sell_orders_by_card:
                    sell_orders_by_card[order.card_type] = [order]
                else:
                    sell_orders_by_card[order.card_type].append(order)

        ## Sort the orders by limit_price
        for _, orders in buy_orders_by_card.items():
            orders.sort(key=lambda x: x.limit_price)
        for _, orders in sell_orders_by_card.items():
            orders.sort(key=lambda x: x.limit_price)

        ## Creating mapping from agentID to its Orders
        agents_orders: dict[UUID, tuple[list[Order], list[Order]]] = {}
        ## agent.UID -> (buy-list, sell-list)
        if self.buy_list and self.sell_list:
            for order in self.buy_list:
                if order.agent_UID not in agents_orders:
                    agents_orders[order.agent_UID] = ([], [])
                agents_orders[order.agent_UID][0].append(order)
            for order in self.sell_list:
                if order.agent_UID not in agents_orders:
                    agents_orders[order.agent_UID] = ([], [])
                agents_orders[order.agent_UID][1].append(order)

        ## Go through all agents and search for orders that meet their requiremnts
        for agent_UID, agent_orders in agents_orders.items():
            self._find_order(agent_UID, agent_orders, buy_orders_by_card, visited)

        # TODO Fix transcation logic: it returns none!!
        if self.buy_list and self.sell_list:
            for order in self.buy_list:
                replace(order, executed=False)
            for order in self.sell_list:
                replace(order, executed=False)

        # Reset the buy/sell lists
        self.sell_list = None
        self.buy_list = None

    def _find_order(
        self,
        agent_UID: UUID,
        agent_orders: tuple[list[Order], list[Order]],
        all_sell_orders: dict[Card, list[Order]],
        visited: set,
    ) -> bool:
        """The function searching for a buy/sell order that meets the card and limit_price requirement"""
        if agent_UID in visited:
            return False
        agent_buy_orders = agent_orders[0]
        for bid in agent_buy_orders:  # For all agent bids
            for offer in all_sell_orders[bid.card_type]:  # For all offers
                if bid.limit_price >= offer.limit_price:
                    if offer.agent_type == AgentType.PLAYER:
                        successful_execution = _find_order(
                            offer.agent_UID,
                        )


class MarketSimple(Market):
    def __init__(self):
        super().__init__(name="simple")
