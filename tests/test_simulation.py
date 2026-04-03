import pytest
from cse6730_project.utils import logger
from cse6730_project.simulation import Simulation
from cse6730_project.config import RNG_SEED
from cse6730_project.agents import Player


@pytest.fixture
def basicSimulation():
    return Simulation(
        market=None, num_players=100, num_scalpers=10, seed=RNG_SEED, num_ticks=2
    )


class TestSimulation:
    def test_init(self, basicSimulation):
        """
        A basic simulation initializes with no market and 100 agents
        """
        assert len(basicSimulation.players) == 100
        assert basicSimulation.players[69].UID == 69
        assert len(basicSimulation.scalpers) == 10

    def test_run(self, basicSimulation):
        basicSimulation.run()
        matchA = basicSimulation.matches[0][0].UID
        matchB = basicSimulation.matches[0][1].UID
        logger.info(
            f"Match at index 0 [player.UID, player.UID] = [{matchA} , {matchB}]"
        )

        samplePlayer: Player = basicSimulation.players[11]
        logger.info(f"Sample Player: {samplePlayer.UID}")
        logger.info(f"{samplePlayer.UID}'s history: {samplePlayer.history}")
