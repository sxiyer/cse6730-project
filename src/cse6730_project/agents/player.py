from uuid import UUID
import random

from base import Agent
from ..models import Card

class Player(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)
        
    def shuffleDeck(self) -> list[Card]:
        cards = []
        
        for card, count in self.deck.items():
            cards.extend([card] * count)
            
        random.shuffle(cards)
        
        return cards