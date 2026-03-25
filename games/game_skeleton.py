from abc import ABC, abstractmethod


class Game(ABC):

    @abstractmethod
    def choose_players(self):
        pass
