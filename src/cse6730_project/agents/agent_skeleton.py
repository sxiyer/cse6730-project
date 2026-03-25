from abc import ABC, abstractmethod


class Agent(ABC):

    def __init__(self):
        self.deck = list()
        self.money: int = 0

    @abstractmethod
    def buy(self):
        pass

    @abstractmethod
    def sell(self):
        pass
