from typing import Callable
from uuid import UUID, uuid4
from dataclasses import replace
from functools import wraps

import random
import pytest

from cse6730_project.models import AgentType, Order, OrderType, Card
from cse6730_project.utils import logger
from cse6730_project.simulation import Simulation
from cse6730_project.config import RNG_SEED
from cse6730_project.utils import rng_rand
from cse6730_project.agents import Player
from cse6730_project.ode.ode import OdeRPS
from cse6730_project.visualization import ODEVisualizer
from cse6730_project.market import Market, MarketCommon
from cse6730_project.config import NUM_PLAYERS, NUM_SCALPERS, NUM_TICKS


@pytest.fixture
def basicMarket() -> Market:
    """Generate a common market"""
    return MarketCommon()


@pytest.fixture
def basicSimulation() -> Simulation:
    # Generate a distribution of players and scalpers
    rng_rand.seed(RNG_SEED)
    return Simulation(
        market=None,
        num_players=NUM_PLAYERS,
        num_scalpers=NUM_SCALPERS,
        seed=RNG_SEED,
        num_ticks=NUM_TICKS,
    )


@pytest.fixture
def basicODERPS(basicSimulation: Simulation) -> OdeRPS:

    return OdeRPS(
        t_interval=(0, 100),
        t_eval=[0, 100, 500],
        initial_counts=basicSimulation.get_card_counts(agent_type=AgentType.PLAYER),
    )


@pytest.fixture
def SimpleOrders() -> tuple[list[Order], list[Order]]:
    """Generate 10 buy and sell orders of each card. The bid price > offer price"""
    orders: tuple[list[Order], list[Order]] = ([], [])

    for card in Card:
        for label in range(40):
            ## Create 10 bids for the same card
            bid_holder: list[Order] = []
            offer_holder: list[Order] = []

            def bid_callback(bid_holder=bid_holder) -> int:
                bid = bid_holder[0]
                if bid.executed:
                    return 1
                elif bid.executed is None:
                    return -10
                return -1

            def offer_callback(offer_holder=offer_holder) -> int:
                offer = offer_holder[0]
                if offer.executed:
                    return 1
                elif offer.executed is None:
                    return -10
                return -1

            bid = replace(
                Order(
                    UUID(int=label),
                    OrderType.BUY,
                    card,
                    2,
                    uuid4(),
                    None,
                    None,
                    AgentType.SCALPER,
                ),
                callback=bid_callback,
            )
            offer = replace(
                Order(
                    UUID(int=label),
                    OrderType.SELL,
                    card,
                    1,
                    uuid4(),
                    None,
                    None,
                    AgentType.SCALPER,
                ),
                callback=offer_callback,
            )

            bid_holder.append(bid)
            offer_holder.append(offer)

            orders[0].append(bid)
            orders[1].append(offer)

    return orders


class TestMakert:
    def test_market_clear(
        self, basicMarket: Market, SimpleOrders: tuple[list[Order], list[Order]]
    ) -> None:
        # Generate a list of sell and buy orders
        logger.info("In market")
        bids, offers = SimpleOrders
        basicMarket.insert_orders(bids, offers)

        basicMarket.clear()

        counter: int = 0
        for order in bids + offers:
            assert order.callback is not None
            if order and order.callback:
                counter += order.callback()

        assert counter == len(bids + offers)
