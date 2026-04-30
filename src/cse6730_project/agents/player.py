from dataclasses import replace
from abc import abstractmethod
from typing import Callable
from uuid import UUID
import random
import numpy as np

from ..models import (
    Card,
    PlayerBehavior,
    CardPrices,
    Order,
    GameResultType,
    OrderType,
    AgentType,
)

from ..config import PAYOFF_NP
from .seeding import seed_single_random, SeedFunction
from ..utils import rng_rand, logger
from .base import Agent

def _deck_to_norm_vector(deck: dict[Card,int]) -> np.ndarray:
    counts = np.array([deck.get(card,0) for card in list(Card)], dtype=float)
    total = counts.sum()
    
    if total == 0:
        return np.ones(3) / 3
    return counts/total

class Player(Agent):
    # TODO: Implement a generator function that will seed the player's deck that
    # can be swapped for different deck distribution functions. Use yielding to
    # track and specify different populations of players getting different
    # seeding functions for their decks
    def __init__(
        self,
        uid: UUID,
        money: float = 0.0,
        seed_deck: SeedFunction = seed_single_random(),
    ):
        super().__init__(uid, agent_type=AgentType.PLAYER, money=money)
        self.PlayerBehavior: PlayerBehavior = PlayerBehavior.NONE
        self.history: list[tuple[GameResultType, UUID, dict[Card, int]]] = []
        self._seed_fn = seed_deck

        seed_deck(self.deck)

    def shuffleDeck(self) -> list[Card]:
        cards = []
        for card, count in self.deck.items():
            cards.extend([card] * count)

        random.shuffle(cards)

        return cards

    def wake_up_agent(self, card_prices: CardPrices) -> tuple[list[Order], list[Order]]:
        """The function takes in the current value of all three cards
        and returns a function to allow the simulation to update the
        agent's deck and money
        A player can only post a single buy/sell order
        tupe[list[Order], list[Order]]: Buy and Sell Orders
        """

        orders: tuple = self.update_state()

        buy_order, sell_order = orders

        if buy_order and sell_order:
            return (buy_order, sell_order)
        elif buy_order:
            return (buy_order, [])
        elif sell_order:
            return ([], sell_order)
        else:
            return ([], [])

    def _create_order(self, order: Order) -> Order:

        def update_agent() -> None:
            if order and order.executed and order.order_type == OrderType.BUY:
                self.deck[order.card_type] += order.quantity
                self.money -= order.exchange_price * order.quantity
            if order and order.executed and order.order_type == OrderType.SELL:
                self.deck[order.card_type] -= order.quantity
                self.money += order.exchange_price * order.quantity

        order = replace(order, callback=update_agent)

        return order

    def update_game_results(self, result: tuple[GameResultType,UUID, dict[Card,int]]) -> None:
        """Returns a function to update the agent on the result of the game"""
        self.history.append(result)

    @abstractmethod
    def update_state(self, card_counts: dict[Card, int]) -> tuple[list[Order], list[Order]]:
        pass

    def get_game_results(self) -> list[GameResultType]:
        return self.history

    def _buy_order(self, card_type: Card, limit_price: float) -> Order | None:
        order = Order(
            order_type=OrderType.BUY,
            card_type=card_type,
            limit_price=limit_price,
            order_UID=None,
            callback=None,
            agent_UID=self.UID,
            executed=None,
        )
        return order

    def _sell_order(self, card_type: Card, limit_price: float) -> Order | None:
        order = Order(
            order_type=OrderType.SELL,
            card_type=card_type,
            limit_price=limit_price,
            order_UID=None,
            callback=None,
            agent_UID=self.UID,
            executed=None,
        )
        return order


class PlayerMutator(Player):
    def __init__(self, uid, money=0.0, p: float = 1.0, seed_deck=seed_single_random()):
        super().__init__(uid, money, seed_deck)
        self.PlayerBehavior = PlayerBehavior.MUTATOR

    def update_state(self, card_counts: dict[Card, int]) -> tuple[list[Order], list[Order]]:
        # sample the current deck for a card to mutate
        owned_cards = [card for card, count in self.deck.items() if count > 0]
        if not owned_cards:
            return ([], [])

        sample1 = rng_rand.choice(owned_cards)

        # find the set opposite of the selected card
        all_cards = list(Card)
        comp = [card for card in all_cards if card != sample1]

        # sample the opposite set
        sample2 = rng_rand.choice(comp)

        self.deck[sample1] -= 1

        if sample2 not in self.deck:
            self.deck[sample2] = 0

        self.deck[sample2] += 1
        buy_order = []
        sell_order = []

        buy_order.append(self._buy_order(card_type=sample2, limit_price=1.0))
        sell_order.append(self._sell_order(card_type=sample1, limit_price=1.0))

        orders = (buy_order, sell_order)
        # place a sell order to sell the first card
        # place a buy order to get the new card
        return orders


class PlayerCopycat(Player):
    def __init__(self, uid, money=0.0, seed_deck=seed_single_random()):
        super().__init__(uid, money, seed_deck)
        self.PlayerBehavior = PlayerBehavior.COPYCAT

    def update_state(self, card_counts: dict[Card, int]) -> tuple[list[Order], list[Order]]:
        buy_order = []
        sell_order = []

        d : np.ndarray = _deck_to_norm_vector(self.deck)
        x : np.ndarray = _deck_to_norm_vector(card_counts)
        orders = (buy_order, sell_order)
        myUID = str(self.UID)

        last_history = self.history[-1]
        last_game_result, last_opponent, last_deck = last_history

        if last_game_result == GameResultType.LOSS:
            logger.debug(f"I lost to {last_deck},\n changing my deck: {self.deck}")
            self.deck = last_deck.copy()
            logger.debug(f"{self.deck}")

        logger.debug(f"{last_game_result}")
        logger.debug(f"{GameResultType.LOSS}")
        logger.debug(f"{myUID[-10:]} MY LAST HISTORY : {last_history}\n")
        return orders
