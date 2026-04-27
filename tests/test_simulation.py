from uuid import UUID

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


@pytest.fixture
def basicMarket() -> Market:
    """Generate a common market"""
    return MarketCommon()


@pytest.fixture
def basicSimulation() -> Simulation:
    # Generate a distribution of players and scalpers
    rng_rand.seed(RNG_SEED)
    return Simulation(
        market=None, num_players=100, num_scalpers=10, seed=RNG_SEED, num_ticks=2
    )


@pytest.fixture
def basicODERPS(basicSimulation: Simulation) -> OdeRPS:

    return OdeRPS(
        t_interval=(0, 100),
        t_eval=[0, 100, 500],
        initial_counts=basicSimulation.get_card_counts(agent_type=AgentType.PLAYER),
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
        cardcounts_players = basicSimulation.get_card_counts(AgentType.PLAYER)
        logger.info(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation.get_card_counts(AgentType.SCALPER)
        logger.info(f"Cards in posession of scalpers: {cardcounts_scalpers}")

    def test_ode(self, basicSimulation: Simulation, basicODERPS: OdeRPS) -> None:
        cardcounts_players = basicSimulation.get_card_counts(AgentType.PLAYER)
        player_pops_int = basicSimulation.get_player_populations("int")
        player_pops_float = basicSimulation.get_player_populations("float")
        logger.info(f"Player pop int : {player_pops_int} \n Player pop float : {player_pops_float}")
        logger.info(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation.get_card_counts(AgentType.SCALPER)
        logger.info(f"Cards in posession of scalpers: {cardcounts_scalpers}")
        odeSol = basicODERPS.SolveODE()
        logger.info(f"Got ODE solution w/ data point count = {len(odeSol.y)}")
        # logger.debug(f"{odeSol.y}")

        logger.info("Plotting ODE...")
        ODEViz = ODEVisualizer()
        ODEViz.save_fig_ode(odeSol.t, odeSol.y, simparams=None)


class TestMakert:
    def test_market(self, basicMarket: Market) -> None:
        # Generate a list of sell and buy orders
        sell_orders = []
        buy_orders = []
