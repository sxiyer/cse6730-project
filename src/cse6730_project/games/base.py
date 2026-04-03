from enum import Enum
from abc import ABC, abstractmethod

from  ..models import Card 
from ..config import PAYOFF
from ..agents import Player

class GameResultType(Enum):
    WIN = "win"     # somebody won
    LOSS = "loss"   # here for losers to know they lost
    TIE = "tie"     # tie

class Game(ABC):
    def __init__(self, player1:Player, player2:Player, tick: int):
        self.result: GameResultType | None = None
        self.loser: Player| None = None
        self.winner: Player | None = None
        self.tick: int = tick
        self.players: tuple[Player,Player] = (player1, player2)
        self.rounds_played: int = 0
        
    def resolveRPS(self, play1: tuple[Player, Card], play2: tuple[Player,Card]) -> GameResultType:
        player1, card1 = play1
        player2, card2 = play2
        
        if card1 == card2:
            return GameResultType.TIE
        elif PAYOFF.get((card1,card2)):
            self.winner = player1
            self.loser = player2
            return GameResultType.WIN
        else:
            self.winner = player2
            self.loser = player1
            return GameResultType.WIN
        
    @abstractmethod
    def play(self) -> GameResultType:
        pass
    
    @property
    def player1(self) -> Player:
        return self.players[0]
    
    @property
    def player2(self) -> Player:
        return self.players[1]
    
        