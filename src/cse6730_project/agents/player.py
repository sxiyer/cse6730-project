from dataclasses import replace
from abc import abstractmethod
from typing import Callable
from uuid import UUID
import random

from ..models import Card, PlayerBehavior, CardPrices, Order, GameResultType, OrderType
from .seeding import seed_single_random, SeedFunction
from ..utils import rng_rand
from .base import Agent


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
        super().__init__(uid, money)
        self.PlayerBehavior: PlayerBehavior = PlayerBehavior.NONE
        self.history: list[GameResultType] = []
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

        
        buy_order = self._buy_order(card_prices)
        sell_order = self._sell_order(card_prices)

        if buy_order and sell_order:
            return ([buy_order], [sell_order])
        elif buy_order:
            return ([buy_order], [])
        elif sell_order:
            return ([], [sell_order])
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

    def update_game_results(self, result: GameResultType) -> None:
        """Returns a function to update the agent on the result of the game"""
        self.history.append(result)

    def update_state(self) -> None:
        pass

    def get_game_results(self) -> list[GameResultType]:
        return self.history

    def _buy_order(
        self, card_type: Card, limit_price: float
    ) -> Order | None:
        order = Order(
            order_type=OrderType.BUY,
            card_type=card_type,
            limit_price=limit_price,
            order_UID=None,
            callback=None,
            agent_UID=self.UID,
            executed= None
        )
        return order

    def _sell_order(
        self, card_type: Card, limit_price: float
    ) -> Order | None:
        order = Order(
            order_type=OrderType.SELL,
            card_type=card_type,
            limit_price=limit_price,
            order_UID=None,
            callback=None,
            agent_UID=self.UID,
            executed= None
        )
        return order


class MutatorPlayer(Player):
    def __init__(self, uid, money=0.0, p: float = 1.0, seed_deck=seed_single_random()):
        super().__init__(uid, money, seed_deck)
        self.PlayerBehavior = PlayerBehavior.MUTATOR

    def update_state(self) -> None:
        # sample the current deck for a card to mutate
        deck = list(self.deck)
        sample1 = rng_rand.choice(deck)
        
        # find the set opposite of the selected card
        comp = self.deck.copy()
        comp.pop(sample1)
        
        # sample the opposite set
        comp = list(comp)
        sample2 = rng_rand.choice(comp)
        
        self._sell_order(card_type=sample1, limit_price=1.0)
        self._buy_order(card_type=sample2, limit_price=1.0)
        # place a sell order to sell the first card
        # place a buy order to get the new card
        return super().update_state()


class CopycatPlayer(Player):
    def __init__(self, uid, money=0.0, seed_deck=seed_single_random()):
        super().__init__(uid, money, seed_deck)
        self.PlayerBehavior = PlayerBehavior.COPYCAT

    def update_state(self) -> None:

        return super().update_state()
