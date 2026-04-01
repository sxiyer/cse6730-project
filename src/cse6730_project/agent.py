from cards import Card
from random import random

class Agent:
    def __init__(self, uid:int, money: float = 0.0):
        self.UID:int = uid
        self.money: float = money
        self.deck: dict[Card, int] = {card: 0 for card in Card}
    
    def decide_sell(self):
        pass
    
    def decide_buy(self):
        pass
    
class Player(Agent):
    def __init__(self, uid:int, money: float = 0.0):
        super().__init__(uid, money)
        
    def shuffleDeck() -> list[Card]:
        cards = []
        
        for card, count in self.deck.items():
            cards.extend([card] * count)
            
        random.shuffle(cards)
        
        return cards
    
    
    
class Scalper(Agent):
    def __init__(self, uid:int, money: float = 0.0):
        super().__init__(uid, money)
    pass