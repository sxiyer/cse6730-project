from uuid import UUID

from .player import Player
from ..models import Card
from ..utils import rng_rand


class PlayerOneCard(Player):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)
        card: Card = rng_rand.choice(list(Card))
        self.deck[card] += 1
