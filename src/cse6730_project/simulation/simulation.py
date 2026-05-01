from collections import Counter
from typing import Callable, Literal
from uuid import UUID

import numpy as np

from ..config import (
    RNG_SEED,
    ODE_PARAMS,
    PLAYER_STARTING_MONEY,
    SCALPER_STARTING_MONEY,
    SEED_DECK_WEIGHTS,
)
from ..agents.seeding import seed_weighted, SeedFunction, seed_single_random
from ..models import (
    AgentType,
    CardPrices,
    Order,
    TickSnapShot,
    GameResultType,
    Card,
    PlayerBehavior,
)
from ..agents import Agent, Player, Scalper, PlayerMutator, PlayerCopycat
from ..games import Game, GameOneCard
from ..market import Market
from ..utils import logger


def _proportional_counts(weights: dict, total: int) -> dict:
    """Convert float/int weights to exact integer counts summing to `total`.

    Uses the largest-remainder method so rounding never under- or over-shoots.
    Works with both float proportions (0.7, 0.3) and integer ratios (3, 1).
    """
    if total == 0:
        return {k: 0 for k in weights}

    denom = sum(weights.values())
    if denom == 0:
        return {k: 0 for k in weights}

    exact = {k: (v / denom) * total for k, v in weights.items()}
    floored = {k: int(f) for k, f in exact.items()}
    remainder = total - sum(floored.values())

    # distribute leftover seats to the types with the largest fractional parts
    fractions = sorted(exact.keys(), key=lambda k: exact[k] - floored[k], reverse=True)
    for k in fractions[:remainder]:
        floored[k] += 1

    return floored


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
        player_type: dict[type[Player], float] | None = None,
        scalper_type: dict[type[Scalper], float] = {Scalper: 1.0},
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
        self.player_map: dict[str, Player] = {}
        self.market: Market | None = market
        self._current_tick: int = 0
        self._history: list = []
        self.matches = []
        if player_type is None:
            player_type = {
                PlayerCopycat: ODE_PARAMS.z,
                PlayerMutator: 1.0 * ODE_PARAMS.mu,
            }
        self.player_type: dict[type[Player], float] = player_type
        self.scalper_type: dict[type[Scalper], float] = scalper_type
        self.games = []
        self.game_type = game_type
        self._game_history = []
        self.rng_np = np.random.default_rng(seed=seed)
        self._card_populations = dict[Card, float]
        self._card_counts = dict[Card, int]

        if num_players < 2:
            raise ValueError("Number of players must be greater than or equal to 2!")
        if num_players % 2 != 0:
            raise ValueError("Number of players must be an even number!")

        counter: int = 0

        # Allocate players using largest-remainder so counts always sum to num_players
        player_counts = _proportional_counts(player_type, num_players)
        for player_cls, count in player_counts.items():
            for _ in range(count):
                pUID = UUID(int=counter)
                p: Player = player_cls(
                    uid=pUID,
                    money=PLAYER_STARTING_MONEY,
                    seed_deck=seed_weighted(SEED_DECK_WEIGHTS),
                )
                p._sim_players = self.num_players
                counter += 1
                self.players.append(p)
                self.player_map[str(pUID)] = p

        # counter is not reset so player and scalper UIDs stay unique
        scalper_counts = _proportional_counts(scalper_type, num_scalpers)
        for scalper_cls, count in scalper_counts.items():
            for _ in range(count):
                s: Scalper = scalper_cls(
                    uid=UUID(int=counter), money=SCALPER_STARTING_MONEY
                )
                counter += 1
                self.scalpers.append(s)

    def _matchPlayers(
        self,
    ) -> None:
        players = np.array(self.players)
        self.rng_np.shuffle(players)

        playersLower_arr = players[0 : self.num_players // 2]
        playersUpper_arr = players[self.num_players // 2 :]

        self.rng_np.shuffle(playersUpper_arr)

        matches_arr = np.column_stack((playersLower_arr, playersUpper_arr))

        self.matches = matches_arr

    def _buildGames(self) -> None:
        self.games.clear()
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
        agent's wake_up_agent() runs update_state (deck evolution) and returns orders.
        2. Submits orders to the market if one is present.
        """
        card_counts = self.get_card_counts(AgentType.PLAYER)
        card_prices = (
            self.market.get_prices()
            if self.market
            else CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        )

        buy_orders: list[Order] = []
        sell_orders: list[Order] = []
        for agent in self.players + self.scalpers:
            agent_buy, agent_sell = agent.wake_up_agent(
                card_prices=card_prices, card_counts=card_counts
            )
            buy_orders.extend(agent_buy)
            sell_orders.extend(agent_sell)

        self._buy_orders = buy_orders
        self._sell_orders = sell_orders

        if self.market is None:
            return
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

    def get_player_populations(
        self, dtype: Literal["int", "float"]
    ) -> dict[PlayerBehavior, int | float]:
        player_pops_int = {behavior: 0 for behavior in PlayerBehavior}
        for player in self.players:
            pbehavior = player.PlayerBehavior
            player_pops_int[pbehavior] += 1

        if dtype == "int":
            return player_pops_int

        total = sum(list(player_pops_int.values()))

        player_pops_float = {behavior: 0.0 for behavior in PlayerBehavior}

        for k, v in player_pops_int.items():
            player_pops_float[k] = v / total

        return player_pops_float

    def get_card_counts(self, agent_type: AgentType) -> dict[Card, int]:
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

    def _compute_card_populations(self) -> None:
        card_pop: dict[Card, float] = {card: 0 for card in Card}
        card_counts = self.get_card_counts(AgentType.PLAYER)
        total_cards = sum(card_counts.values())
        for card, count in card_counts.items():
            card_pop[card] = count / total_cards

        self._card_counts = card_counts
        self._card_populations = card_pop

    def _recordState(self) -> None:
        snapshot = TickSnapShot(
            tick=self._current_tick,
            card_populations=dict(self._card_populations),
            card_prices=self.market.get_prices() if self.market else None,
            order_volume=self.market.get_stock() if self.market else None,
        )
        self._history.append(snapshot)

    def getHistory(self) -> list[TickSnapShot]:
        return self._history

    def get_population_history(self) -> dict[Card, list[float]]:
        result: dict[Card, list[float]] = {card: [] for card in Card}
        for snap in self._history:
            for card in Card:
                result[card].append(snap.card_populations.get(card, 0.0))
        return result

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
        self._compute_card_populations()
        self._recordState()  # Record meaningful info from this tick

    def run(self) -> None:
        for i in range(self._current_tick, self.num_ticks):
            self._step()
            self._current_tick += 1
