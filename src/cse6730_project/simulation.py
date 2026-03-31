from agent import Agent, Player, Scalper
from market import Market
from config import *
from reporting import *

import numpy as np

class Simulation:
    """
    The simulation orchestrator. It matches up players, keeps track of the
    global tick, and organizes when the market updates.
    """
    
    def __init__(self, market: Market | None = None, num_players: int = 2, num_scalpers: int = 0, num_ticks: int = 1, seed: int = 0):
        """
        Initializes a simulation.
        
        args
        ------
        market : Market, optional
            a market defines how transactions are handled between buyers and sellers
        num_players : int
            number of players in this simulation
        num_scalpers :  int
            number of scalpers in this simulation
        num_ticks : int
            the number of ticks this simulation will run for
        
        returns
        ------
        nothing
        """
        self.num_ticks = num_ticks
        self.num_players = num_players
        self.num_scalpers = num_scalpers
        self.players = []
        self.scalpers = []
        self.market = market
        self.current_tick = 0
        self.history = None
        self.matches = []
        self.rng = np.random.default_rng(seed = seed)
        
        assert num_players >= 2, "Number of players must be greater than or equal to 2!"
        assert num_players %2 == 0, "Number of players must be an even number!"

        for i in range(num_players):
            p = Player()
            p.UID = i
            self.players.append(p)

        for i in range(num_scalpers):
            s = Scalper()
            s.UID = i
            self.scalpers.append(s)

    def step(self):
        self.matchPlayers() 
        
    def matchPlayers(self):
        playersLower = self.players[0:self.num_players//2]
        playersUpper = self.players[self.num_players//2 :]

        playersLower_arr = np.array(playersLower)
        playersUpper_arr = np.array(playersUpper)
        
        self.rng.shuffle(playersUpper_arr)
        
        matches_arr = np.column_stack((playersLower_arr, playersUpper_arr))

        self.matches = matches_arr

    def run(self):
        for i in range(self.num_ticks):
            self.step()