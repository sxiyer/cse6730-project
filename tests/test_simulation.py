import pytest
import logging
from simulation import Simulation

@pytest.fixture
def basicSimulation():
    return Simulation(market = None, num_players = 100, num_scalpers = 10, seed = 420)

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
        logging.info(f"Match at index 0 [player.UID, player.UID] = [{matchA} , {matchB}]")