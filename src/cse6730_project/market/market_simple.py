from ..models import Card
from .base import Market


class MarketSimple(Market):
    def __init__(self):
        super().__init__(name="simple")
        self.stock = {card: 1000 for card in Card}
        self.prices = {card: 1.0 for card in Card}

    def submit_order(self, order):
        # Any order is successful
        return True
