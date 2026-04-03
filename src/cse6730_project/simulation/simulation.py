from uuid import UUID

from ..agents import Agent, Player, Scalper
from ..market import Market
from ..config import *
from ..reporting import *
from ..config import RNG_SEED, PLAYER_STARTING_MONEY, SCALPER_STARTING_MONEY
from ..utils import logger, rng_np
from ..games import Game, GameResultType
from ..games.game_onecard import GameOneCard
from ..agents.player_onecard import PlayerOneCard

import numpy as np


class Simulation:
    """
    The simulation orchestrator. It matches up players, keeps track of the
    global tick, and organizes when the market updates.
    """

    def __init__(
        self,
        market: Market | None = None,
        seed: int | None = RNG_SEED,
        num_players: int = 2,
        num_scalpers: int = 0,
        num_ticks: int = 1,
        game_type: type[Game] = GameOneCard,
        player_type: type[Player] = PlayerOneCard,
        scalper_type: type[Scalper] = Scalper,
    ):
        """
        Initializes a simulation.

        args
        ------
        market : Market, optional
            a market defines how transactions are handled between buyers and sellers
        num_players : int
            number of players in this simulation
        num_scalpers :  int
            number of scalpers in this simulation
        num_ticks : int
            the number of ticks this simulation will run for

        returns
        ------
        nothing
        """
        self.num_ticks: int = num_ticks
        self.num_players: int = num_players
        self.num_scalpers: int = num_scalpers
        self.players: list[Player] = []
        self.scalpers: list[Scalper] = []
        self.market: Market | None = market
        self.current_tick: int = 0
        self.history = None
        self.matches = []
        self.game_type = game_type
        self.player_type: type[Player] = player_type
        self.scalper_type: type[Scalper] = scalper_type
        self.games = []
        self.rng_np = np.random.default_rng(seed=seed)

        assert num_players >= 2, "Number of players must be greater than or equal to 2!"
        assert num_players % 2 == 0, "Number of players must be an even number!"

        # Initialize some basic players according to specified player_type

        for i in range(num_players):
            p: Player = self.player_type(uid=UUID(int=i), money=PLAYER_STARTING_MONEY)
            self.players.append(p)

        for i in range(num_scalpers):
            s: Scalper = self.scalper_type(
                uid=UUID(int=i), money=SCALPER_STARTING_MONEY
            )
            self.scalpers.append(s)

    def step(self):
        self.matchPlayers()  # Matchmaker to create pairs of players
        self.buildGames()  # Setup games between players
        self.playGames()  # All games play
        self.playersUpdate()  # Players review outcomes, submit orders (or not)
        self.marketClears()  # Market processes orders
        self.recordState()  # Record meaningful info from this tick

    def matchPlayers(self) -> None:
        playersLower = self.players[0 : self.num_players // 2]
        playersUpper = self.players[self.num_players // 2 :]

        playersLower_arr = np.array(playersLower)
        playersUpper_arr = np.array(playersUpper)

        self.rng_np.shuffle(playersUpper_arr)

        matches_arr = np.column_stack((playersLower_arr, playersUpper_arr))

        self.matches = matches_arr

    def buildGames(self) -> None:
        for match in self.matches:
            logger.debug(f"Building match at tick {self.current_tick}")

            player1 = match[0]
            player2 = match[1]

            logger.debug(
                f"Found player1 (UID: {player1.UID}) and player2 (UID: {player2.UID}), creating game..."
            )

            game = self.game_type(player1, player2, self.current_tick)

            logger.debug(f"Game created, adding to games, GAME: {game}")
            self.games.append(game)

    def playGames(self) -> None:
        for game in self.games:
            game.play()
            if game.result == GameResultType.WIN:
                winner = game.winner
                loser = game.loser
                logger.debug(
                    f"Game {game} complete!\nWinner: {winner.UID}\nLoser: {loser.UID}"
                )
            else:
                logger.debug(f"Game {game} complete! Result: TIE")

    def playersUpdate(self) -> None:
        # TODO: Tell the players to place orders based on the outcomes of the games
        pass

    def marketClears(self) -> None:
        # TODO: Market processes orders
        pass

    def recordState(self) -> None:
        # TODO: Record the important information from the current tick
        pass

    def run(self) -> None:
        for i in range(self.num_ticks):
            self.step()
            self.current_tick += 1
