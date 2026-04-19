from uuid import UUID


import pytest

from cse6730_project.models import AgentType, Order, OrderType, Card
from cse6730_project.utils import logger
from cse6730_project.simulation import Simulation
from cse6730_project.config import RNG_SEED
from cse6730_project.agents import Player
from cse6730_project.ode.ode import OdeRPS
from cse6730_project.market import Market, MarketCommon


@pytest.fixture
def basicMarket() -> Market:
    """Generate a common market"""
    return MarketCommon()


@pytest.fixture
def basicSimulation() -> Simulation:
    # Generate a distribution of players and scalpers

    return Simulation(
        market=None, num_players=100, num_scalpers=10, seed=RNG_SEED, num_ticks=2
    )


@pytest.fixture
def basicODERPS(basicSimulation: Simulation) -> OdeRPS:

    return OdeRPS(
        t_interval=(0, 100),
        t_eval=[0, 100, 10],
        initial_counts=basicSimulation._get_card_counts(agent_type=AgentType.PLAYER),
    )


class TestSimulation:
    def test_init(self, basicSimulation: Simulation) -> None:
        """
        A basic simulation initializes with no market and 100 agents
        """
        assert len(basicSimulation.players) == 100  # Check number of players
        assert basicSimulation.players[69].UID == UUID(int=69)
        assert len(basicSimulation.scalpers) == 10

    def test_run(self, basicSimulation) -> None:
        basicSimulation.run()
        matchA = basicSimulation.matches[0][0].UID
        matchB = basicSimulation.matches[0][1].UID
        logger.info(
            f"Match at index 0 [player.UID, player.UID] = [{matchA} , {matchB}]"
        )

        samplePlayer: Player = basicSimulation.players[11]
        logger.info(f"Sample Player: {samplePlayer.UID}")
        logger.info(f"{samplePlayer.UID}'s history: {samplePlayer.history}")

    def test_cardcounts(self, basicSimulation: Simulation) -> None:
        cardcounts_players = basicSimulation._get_card_counts(AgentType.PLAYER)
        logger.debug(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation._get_card_counts(AgentType.SCALPER)
        logger.debug(f"Cards in posession of scalpers: {cardcounts_scalpers}")

    def test_ode(self, basicSimulation: Simulation, basicODERPS: OdeRPS) -> None:
        odeSol = basicODERPS.SolveODE()
        logger.info(f"Got ODE solution w/ data point count = {len(odeSol.y)}")
        logger.debug(f"{odeSol.y}")

    def test_market(self, basicMarket: Market) -> None:
        # Generate a list of sell and buy orders
        sell_orders = [
            Order(
                agent_UID=UUID(int=i),
                order_type=OrderType.SELL,
                card_type=Card.ROCK,
                limit_price=10,
            )
            for i in range(10)
        ]
        buy_orders = [
            Order(
                agent_UID=UUID(int=i),
                order_type=OrderType.SELL,
                card_type=Card.ROCK,
                limit_price=10,
            )
            for i in range(10)
        ]

        basicMarket.insert_orders(buy_orders=buy_orders, sell_orders=sell_orders)

        assert basicMarket.buy_list is not None
        assert basicMarket.sell_list is not None

        basicMarket.clear()

        assert basicMarket.buy_list is None
        assert basicMarket.sell_list is None
