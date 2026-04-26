from collections import Counter
from typing import Callable
from uuid import UUID

import numpy as np

from ..models import AgentType, Order, TickSnapShot, GameResultType, AgentSpecs
from ..config import RNG_SEED, PLAYER_STARTING_MONEY, SCALPER_STARTING_MONEY
from ..agents import Agent, Player, Scalper, PlayerOneCard
from ..games import Game, GameOneCard
from ..market import Market
from ..utils import logger
from ..reporting import *
from ..config import *


class Simulation:
    """
    The simulation orchestrator. It matches up players, keeps track of the
    global tick, and organizes when the market updates.
    """

    def __init__(
        self,
        *,
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
        self._buy_orders: list
        self._sell_orders: list
        self.num_ticks: int = num_ticks
        self.num_players: int = num_players
        self.num_scalpers: int = num_scalpers
        self.players: list[Player] = []
        self.scalpers: list[Scalper] = []
        self.market: Market | None = market
        self._current_tick: int = 0
        self._history: list = []
        self.matches = []
        self.player_type: dict[type[Player], int] = player_type
        self.scalper_type: dict[type[Scalper], int] = scalper_type
        self.games = []
        self.game_type = game_type
        self._game_history = []
        self.rng_np = np.random.default_rng(seed=seed)

        assert num_players >= 2, "Number of players must be greater than or equal to 2!"
        assert num_players % 2 == 0, "Number of players must be an even number!"

        # Initialize some basic players according to specified player_type

        denominator: int = sum(player_type.values())
        counter: int = 0
        for player, population in player_type.items():
            ratio = self.num_players * (population // denominator)
            for _ in range(ratio):
                p: Player = player(uid=UUID(int=counter), money=PLAYER_STARTING_MONEY)
                counter += 1
                self.players.append(p)

        denominator = sum(scalper_type.values())
        # counter = 0 Don't resest the counter to have unique player and scalper ids
        for scalper, population in scalper_type.items():
            ratio = self.num_scalpers * population // denominator
            for _ in range(ratio):
                s: Scalper = scalper(
                    uid=UUID(int=counter), money=SCALPER_STARTING_MONEY
                )
                counter += 1
                self.scalpers.append(s)

    def _matchPlayers(
        self,
    ) -> None:
        playersLower = self.players[0 : self.num_players // 2]
        playersUpper = self.players[self.num_players // 2 :]

        playersLower_arr = np.array(playersLower)
        playersUpper_arr = np.array(playersUpper)

        self.rng_np.shuffle(playersUpper_arr)

        matches_arr = np.column_stack((playersLower_arr, playersUpper_arr))

        self.matches = matches_arr

    def _buildGames(self) -> None:
        for match in self.matches:
            logger.debug(f"Building match at tick {self._current_tick}")

            player1 = match[0]
            player2 = match[1]

            logger.debug(
                f"Found player1 (UID: {player1.UID}) and player2 (UID: {player2.UID}), creating game..."
            )

            game = self.game_type(player1, player2, self._current_tick)

            logger.debug(f"Game created, adding to games, GAME: {game}")
            self.games.append(game)

    def _playGames(self) -> None:
        for game in self.games:
            game.play()
            if game.result == GameResultType.WIN:
                winner = game.winner
                loser = game.loser
                logger.debug(
                    f"Game {game} complete!\nWinner: {winner.UID}\nLoser: {loser.UID}"
                )
            else:
                winner = game.winner
                loser = game.loser

                logger.debug(f"Game {game} complete! Result: TIE")

    def _agentUpdate(self) -> None:
        """
        1. Calls wake_up_agent() on every agent (players + scalpers). Each
        agen'ts wake_up_agent() runs buy_order() and sell_order() and stores
        non-None results in self.pending_orders.
        2. Immediately submits those
        pending orders to the market and clears the list.
        """
        if self.market is None:
            return

        # Call all agents and collect their orders
        buy_orders: list[Order] = []
        sell_orders: list[Order] = []
        card_prices = self.market.get_prices()
        for agent in self.players + self.scalpers:
            buy_orders, sell_orders = agent.wake_up_agent(card_prices)

        self._buy_orders = buy_orders
        self._sell_orders = sell_orders
        # Submit all orders to the market
        self.market.insert_orders(buy_orders, sell_orders)

    def _marketClears(self) -> None:
        """
        1. Calls market.clear(), which matches orders per card type
        2. After clearing, reads market.executed_trades and
        applies them back to agents
        """
        if self.market is None:
            return

        # Tell the market to execute trades
        self.market.clear()

        # Update agents' decks and money
        for order in self._buy_orders + self._sell_orders:
            order.callback()

        self._buy_orders = []
        self._sell_orders = []

    def get_player(self, id: UUID) -> Agent | None:
        return self.players[int(id)]

    def _get_card_counts(self, agent_type: AgentType) -> dict[Card, int]:
        card_counts: dict[Card, int] = {card: 0 for card in Card}

        match agent_type:
            case AgentType.ALL:
                agents = self.scalpers + self.players
            case AgentType.SCALPER:
                agents = self.scalpers
            case AgentType.PLAYER:
                agents = self.players
            case _:
                agents = []

        for agent in agents:
            temp_count = dict(Counter(agent.deck))
            for key, value in temp_count.items():
                card_counts[key] += value

        return card_counts

    def _recordState(self) -> None:
        """
        game_history: {player_x: [wins, losses]}
        player_card_history: {player_x: list[Deck]}
        scalper_card_history: {scalper_x: list[Deck]}
        cards_values: list[dict[Cards, value]]
        """
        # TODO: Record the important information from the current tick
        if self.market is None:
            return

        snapshot = TickSnapShot(
            tick=self._current_tick,
            card_prices=self.market.get_prices(),
            order_volume=self.market.get_stock(),
            top_twenty_players=[],
            top_twenty_scalper=[],
        )
        self._history.append(snapshot)

    def getHistory(self) -> list[TickSnapShot]:
        return self._history

    def next_tick(self) -> None:
        self._step()
        self._current_tick += 1

    def _step(self) -> None:
        self._matchPlayers()  # Matchmaker to create pairs of players
        """
        1. divide the players into two groups
        2. Shuffle the second group's order
        3. create pairs from both groups
        4. return the a list of groups
        """
        self._buildGames()  # Setup games between players
        """
        1. for every pair of players, create an instance of a game with the two players 
        2. return a list of games 
        """
        self._playGames()  # All games play
        """
        1. play every game
        2. store who won/lost
        """
        self._agentUpdate()  # Players review outcomes, submit orders (or not)
        """
        1. for every agent (player + scalper), get their orders (list of sell/buy)
        2. store the agents' callback function in a dict that maps their UUID to their callback
        """
        self._marketClears()  # Market processes orders
        """
        1. tell the market to execute trades and return a list of transactions 
        2. update all agents on their transactions 
        """
        self._recordState()  # Record meaningful info from this tick

    def run(self) -> None:
        for i in range(self._current_tick, self.num_ticks):
            self._step()
            self._current_tick += 1
