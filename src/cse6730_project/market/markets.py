from collections import defaultdict
from dataclasses import replace
from typing import cast
from operator import neg
from enum import Enum
from uuid import UUID

from sortedcontainers import SortedSet, SortedDict

from ..models import Card, Order, OrderType, AgentType
from ..utils import logger
from . import Market


class OrderStatus(Enum):
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"


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
                    order.executed = False
            if self.sell_list:
                for order in self.sell_list:
                    order.executed = False
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

        logger.info("Executing trade")

        dfs_stack: set = set()  # only used for players

        ## Create Mapping for Card types:

        offers: dict[Card, dict] = dict(
            {
                card: dict(
                    {
                        OrderStatus.AVAILABLE: SortedSet(),
                        OrderStatus.PENDING: SortedSet(),
                    }
                )
                for card in Card
            }
        )

        # Insert all of the offers
        for offer in self.sell_list:
            assert offer.callback is not None
            offers[offer.card_type][OrderStatus.AVAILABLE].add(offer)

        ## Creating mapping from agentID to its bids by decreasing order
        agents_bids: defaultdict[UUID, SortedSet] = defaultdict(lambda: SortedSet())
        for order in self.buy_list:
            assert order.callback is not None
            agents_bids[order.agent_UID].add(order)

        ## Go through all agents and search for orders that meet their requiremnts
        # for offer in offers:

        for ids, bids in dict(agents_bids).items():
            if bids:
                agent_type: AgentType = cast(Order, bids[-1]).agent_type
                assert isinstance(agent_type, AgentType)

                bought = self._find_order(
                    ids, agents_bids, offers, dfs_stack, agent_type
                )

        # Reset the buy/sell lists
        self.sell_list = None
        self.buy_list = None

    def _find_order(
        self,
        agent_UID: UUID,
        agent_orders: defaultdict[UUID, SortedSet],
        offers: dict[Card, dict],
        dfs_stack: set,
        agent_type: AgentType,
    ) -> bool:
        """The function searching for offers that meets the bid requirements"""

        if agent_type == AgentType.PLAYER and agent_UID in dfs_stack:
            dfs_stack.remove(agent_UID)
            return True

        ## Pop the highest bid if there is any
        if agent_orders[agent_UID]:
            bid = agent_orders[agent_UID].pop()
        elif agent_type == AgentType.PLAYER:
            return False
        else:
            return True

        ## Search the AVAILABLE offers
        index: int = 0
        while offers[bid.card_type][OrderStatus.AVAILABLE]:
            num_offers = len(offers[bid.card_type][OrderStatus.AVAILABLE])
            if index >= num_offers:
                break
            offer = offers[bid.card_type][OrderStatus.AVAILABLE][index]
            if (
                bid.limit_price >= offer.limit_price
                and bid.agent_UID != offer.agent_UID
                and offer.agent_UID not in dfs_stack
            ):
                ## Remove offer from AVAILABLE set
                offer = offers[bid.card_type][OrderStatus.AVAILABLE].pop(index)
                ## Add players to the stack set
                if agent_type == AgentType.PLAYER:
                    dfs_stack.add(agent_UID)

                ## Try to execute the order
                bought: bool = self._find_order(
                    offer.agent_UID, agent_orders, offers, dfs_stack, offer.agent_type
                )
                ## Remove offer from PENDING
                if bought:
                    ## Set the transaction as successful
                    offer.executed = True
                    bid.executed = True
                    ## Update the agent
                    offer.callback()
                    bid.callback()

                    if agent_type == AgentType.PLAYER and agent_UID not in dfs_stack:
                        return False
                    else:
                        return True
                else:
                    ## Set the transaction as failed
                    if agent_type == AgentType.PLAYER:
                        dfs_stack.remove(agent_UID)
                    offer.executed = False
                    bid.executed = False
                    ## Updat the agent
                    offer.callback()
                    bid.callback()
            index += 1

        ## Check the PENDING offers
        index: int = 0
        while offers[bid.card_type][OrderStatus.AVAILABLE]:
            num_offers = len(offers[bid.card_type][OrderStatus.AVAILABLE])
            if index >= num_offers:
                break
            offer = offers[bid.card_type][OrderStatus.AVAILABLE][index]
            if (
                bid.limit_price >= offer.limit_price
                and bid.agent_UID != offer.agent_UID
                and offer.agent_UID in dfs_stack
            ):
                ## Remove offer from AVAILABLE set
                offer = offers[bid.card_type][OrderStatus.AVAILABLE].pop(index)
                ## Add players to the stack set
                if agent_type == AgentType.PLAYER:
                    dfs_stack.add(agent_UID)

                ## Try to execute the order
                bought = self._find_order(
                    offer.agent_UID, agent_orders, offers, dfs_stack, offer.agent_type
                )
                if bought:
                    ## Set the transaction as successful
                    offer.executed = True
                    bid.executed = True
                    ## Update the agent
                    offer.callback()
                    bid.callback()
                    if agent_type == AgentType.PLAYER and agent_UID not in dfs_stack:
                        return False
                    else:
                        return True
                else:
                    ## Set the transaction as fail
                    if agent_type == AgentType.PLAYER:
                        dfs_stack.remove(agent_UID)
                    offer.executed = False
                    bid.executed = False
                    ## Update the agent
                    offer.callback()
                    bid.callback()
            index += 1
        bid.executed = False
        bid.callback()

        if agent_type == AgentType.PLAYER:
            return False
        else:
            return True


class MarketSimple(Market):
    def __init__(self):
        super().__init__(name="simple")
