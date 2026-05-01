from typing import Callable
from uuid import UUID, uuid4

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
def simpleOrders(callback: Callable) -> tuple[list[Order], list[Order]]:
    """Generate 10 buy and sell orders of each card. The bid price > offer price"""
    orders: tuple[list[Order], list[Order]] = ([], [])

    for _ in range(10):
        ## Create 10 bids for the same card
        bid = Order(
            uuid4(),
            OrderType.BUY,
            Card.ROCK,
            2,
            uuid4(),
            callback,
            None,
            AgentType.PLAYER,
        )
        offer = Order(
            uuid4(),
            OrderType.SELL,
            Card.ROCK,
            1,
            uuid4(),
            callback,
            None,
            AgentType.PLAYER,
        )
        orders[0].append(bid)
        orders[1].append(offer)

    return orders


class TestSimulation:
    def test_init(self, basicSimulation: Simulation) -> None:
        """
        A basic simulation initializes with no market and NUM_PLAYERS agents
        """
        assert len(basicSimulation.players) == NUM_PLAYERS  # Check number of players
        assert basicSimulation.players[NUM_PLAYERS // 2].UID == UUID(
            int=NUM_PLAYERS // 2
        )
        assert len(basicSimulation.scalpers) == NUM_SCALPERS

    def test_run(self, basicSimulation: Simulation, basicMarket: Market) -> None:
        basicSimulation.market = basicMarket
        logger.info("==================== BEFORE RUNNING ======================")

        cardcounts_players = basicSimulation.get_card_counts(AgentType.PLAYER)
        logger.info(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation.get_card_counts(AgentType.SCALPER)
        logger.info(f"Cards in posession of scalpers: {cardcounts_scalpers}")

        basicSimulation.run()

        logger.info("==================== AFTER RUNNING ======================")

        cardcounts_players = basicSimulation.get_card_counts(AgentType.PLAYER)
        logger.info(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation.get_card_counts(AgentType.SCALPER)
        logger.info(f"Cards in posession of scalpers: {cardcounts_scalpers}")

        matchA = basicSimulation.matches[0][0].UID
        matchB = basicSimulation.matches[0][1].UID
        logger.info(
            f"Match at index 0 [player.UID, player.UID] = [{matchA} , {matchB}]"
        )

        samplePlayer: Player = basicSimulation.players[0]
        logger.info(f"Sample Player: {samplePlayer.UID}")
        logger.debug(f"{samplePlayer.UID}'s history: {samplePlayer.history}")

    def test_cardcounts(self, basicSimulation: Simulation) -> None:
        cardcounts_players = basicSimulation.get_card_counts(AgentType.PLAYER)
        logger.info(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation.get_card_counts(AgentType.SCALPER)
        logger.info(f"Cards in posession of scalpers: {cardcounts_scalpers}")

    def test_ode(self, basicSimulation: Simulation, basicODERPS: OdeRPS) -> None:
        cardcounts_players = basicSimulation.get_card_counts(AgentType.PLAYER)
        player_pops_int = basicSimulation.get_player_populations("int")
        player_pops_float = basicSimulation.get_player_populations("float")
        logger.info(
            f"Player pop int : {player_pops_int} \n Player pop float : {player_pops_float}"
        )
        logger.info(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation.get_card_counts(AgentType.SCALPER)
        logger.info(f"Cards in posession of scalpers: {cardcounts_scalpers}")
        odeSol = basicODERPS.SolveODE()
        logger.info(f"Got ODE solution w/ data point count = {len(odeSol.y)}")
        # logger.debug(f"{odeSol.y}")

        logger.info("Plotting ODE...")
        ODEViz = ODEVisualizer()
        if isinstance(odeSol.t, list) and isinstance(odeSol.y, list):
            ODEViz.save_fig_ode(odeSol.t, odeSol.y, simparams=None)

    def test_market_interactions(
        self, basicSimulation: Simulation, basicMarket: Market
    ) -> None:
        basicSimulation.market = basicMarket
        basicSimulation.run()


"""
class TestMakert:
    def test_market_clear(
        self, basicMarket: Market, simpleOrders: tuple[list[Order], list[Order]]
    ) -> None:
        # Generate a list of sell and buy orders
        bids, offers = simpleOrders
        basicMarket.insert_orders(bids, offers)
"""
