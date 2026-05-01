from typing import Callable

from ..models import Card
from ..config import MAX_DECK_SIZE
from ..utils import rng_np, logger

SeedFunction = Callable[[dict[Card, int]], None]


def seed_single_random() -> SeedFunction:
    def _seeder(deck: dict[Card, int]):
        card_types = list(Card)
        card = card_types[rng_np.integers(len(card_types))]
        deck[card] += 1

    return _seeder


def seed_weighted(weights: dict[Card, float]) -> SeedFunction:
    total = sum(weights.values())
    card_types = list(weights.keys())
    card_p = [w / total for w in weights.values()]

    if len(card_types) != len(weights):
        logger.error(
            f"Improper weight assignment, got {len(weights)} assignments, expected {len(card_types)} values!"
        )
        raise IndexError

    def _seeder(deck: dict[Card, int]) -> None:
        inds = rng_np.choice(len(card_types), size=MAX_DECK_SIZE, p=card_p)
        for i in inds:
            deck[card_types[i]] += 1

    return _seeder
