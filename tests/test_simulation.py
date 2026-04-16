from uuid import UUID

import pytest

from cse6730_project.models import AgentType
from cse6730_project.utils import logger
from cse6730_project.simulation import Simulation
from cse6730_project.config import RNG_SEED
from cse6730_project.agents import Player


@pytest.fixture
def basicSimulation() -> Simulation:
    # Generate a distribution of players and scalpers

    return Simulation(
        market=None, num_players=100, num_scalpers=10, seed=RNG_SEED, num_ticks=2
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
    
    def test(self, basicSimulation: Simulation) -> None:
        cardcounts_players = basicSimulation._get_card_counts(AgentType.PLAYER)
        logger.debug(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation._get_card_counts(AgentType.SCALPER)
        logger.debug(f"Cards in posession of scalpers: {cardcounts_scalpers}")
        
