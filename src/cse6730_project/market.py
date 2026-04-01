from cards import Card
from order import *
from abc import ABC, abstractmethod

class Market:
    def __init__(self, name:str):
       self.name = name
       self.stock = {card: 0 for card in Card}
       self.prices = {card: 0.0 for card in Card}
       
    @abstractmethod
    def submit_order(self, order: Order) -> bool:
        pass