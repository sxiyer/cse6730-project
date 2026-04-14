from uuid import UUID

from ..agents import Agent, Player, Scalper
from ..market import Market
from ..config import *
from ..reporting import *
from ..config import RNG_SEED, PLAYER_STARTING_MONEY, SCALPER_STARTING_MONEY
from ..utils import logger, rng_np
from ..games import Game, GameResultType
from ..games.game_one_card import GameOneCard
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
        player_type: dict[type[Player], int] = {PlayerOneCard: 1},
        scalper_type: dict[type[Scalper], int] = {Scalper: 1},
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
        self.players: list[Player] = (
            []
        )  # TODO: Change to dict for O(1) access by UID? Or numpy array?
        self.scalpers: list[Scalper] = []
        self.market: Market | None = market
        self.current_tick: int = 0
        self.history: dict[int, dict] = {}
        self.matches = []
        self.game_type = game_type
        self.player_type: dict[type[Player], int] = player_type
        self.scalper_type: dict[type[Scalper], int] = scalper_type
        self.games = []
        self.rng_np = np.random.default_rng(seed=seed)

        assert num_players >= 2, "Number of players must be greater than or equal to 2!"
        assert num_players % 2 == 0, "Number of players must be an even number!"

        # Initialize some basic players according to specified player_type

        denominator: int = sum(player_type.values())
        counter: int = 0
        for player, population in player_type.items():
            ratio = self.num_players * (population // denominator)
            for _ in range(ratio):
                p: Player = player(uid=UUID(int=(counter)), money=PLAYER_STARTING_MONEY)
                counter += 1
                self.players.append(p)

        denominator = sum(scalper_type.values())
        counter = 0
        for scalper, population in scalper_type.items():
            ratio = self.num_players * (population // denominator)
            for _ in range(ratio):
                s: Scalper = scalper(
                    uid=UUID(int=counter), money=SCALPER_STARTING_MONEY
                )
                counter += 1
                self.scalpers.append(s)

    def step(self):
        self.matchPlayers()  # Matchmaker to create pairs of players
        self.buildGames()  # Setup games between players
        self.playGames()  # All games play
        self.agentUpdate()  # Players review outcomes, submit orders (or not)
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

    def agentUpdate(self) -> None:
        for player in self.players:
            player.wake_up_agent()
        for scalper in self.scalpers:
            scalper.wake_up_agent()

    def marketClears(self) -> None:
        if self.market:
            self.market.clear()

    def __getitem__(self):
        pass

    def get_player(self, id: UUID) -> Agent | None:
        return self.players[int(id)]

    def recordState(self) -> dict:
        """
        game_history: {player_x: [wins, losses]}
        player_card_history: {player_x: list[Deck]}
        scalper_card_history: {scalper_x: list[Deck]}
        cards_values: list[dict[Cards, value]]

        """
        return self.history
        # TODO: Record the important information from the current tick

        pass

    def next_tick(self) -> None:
        self.step()
        self.current_tick += 1

    def run(self) -> None:
        for i in range(self.current_tick, self.num_ticks):
            self.step()
            self.current_tick += 1
