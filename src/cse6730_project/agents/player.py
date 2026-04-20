from typing import Callable
from abc import abstractmethod
from uuid import UUID
import random

from .base import Agent
from ..utils import rng_rand
from ..models import Card, PlayerBehavior, CardPrices, Order, GameResultType


class Player(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)
        self.PlayerBehavior: PlayerBehavior = PlayerBehavior.NONE
        self.game_history: list[GameResultType] = []

    def shuffleDeck(self) -> list[Card]:
        cards = []

        for card, count in self.deck.items():
            cards.extend([card] * count)

        random.shuffle(cards)

        return cards

    def wake_up_agent(
        self, card_prices: CardPrices
    ) -> list[tuple[Order | None, Order | None, Callable]] | None:
        """The function takes in the current value of all three cards
        and returns a function to allow the simulation to update the
        agent's deck and money
        A player can only post a single buy/sell order
        """

        buy_order = self._buy_order(card_prices)
        sell_order = self._sell_order(card_prices)

        def update_agent(successful: bool, exchanged_prices: dict[Card, float]) -> None:
            if successful and buy_order:
                self.deck[buy_order.card_type] += buy_order.quantity
                self.money -= exchanged_prices[buy_order.card_type] * buy_order.quantity
            if successful and sell_order:
                self.deck[sell_order.card_type] -= sell_order.quantity
                self.money += (
                    exchanged_prices[sell_order.card_type] * sell_order.quantity
                )

        if self._buy_order and self._sell_order:
            return [(buy_order, sell_order, update_agent)]
        # The agent won't participate
        return None

    def update_game_results(self, result: GameResultType) -> None:
        """Returns a function to update the agent on the result of the game"""
        self.game_history.append(result)

    def get_game_results(self) -> list[GameResultType]:
        return self.game_history

    @abstractmethod
    def _buy_order(self, card_prices: CardPrices) -> Order | None:
        pass

    @abstractmethod
    def _sell_order(self, card_prices: CardPrices) -> Order | None:
        pass


class PlayerOneCard(Player):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)
        card: Card = rng_rand.choice(list(Card))
        self.deck[card] += 1

    def _buy_order(self, card_prices: CardPrices) -> Order | None:
        return None

    def _sell_order(self, card_prices: CardPrices) -> Order | None:
        return None
