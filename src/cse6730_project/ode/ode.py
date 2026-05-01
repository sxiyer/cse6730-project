from scipy.integrate import solve_ivp
from scipy.integrate._ivp.ivp import OdeResult
import numpy as np

from ..utils import logger
from ..config import ODE_PARAMS
from ..models import Card


class OdeRPS:
    def __init__(
        self,
        Z_COPYCAT_RATE: float = ODE_PARAMS.z,
        MU_MUTATION_RATE: float = ODE_PARAMS.mu,
        initial_counts: dict[Card, int] = {},
        t_interval: tuple[int, int] = (
            ODE_PARAMS.t_interval.start,
            ODE_PARAMS.t_interval.end,
        ),
        t_eval: list[int] = [
            ODE_PARAMS.t_eval.start,
            ODE_PARAMS.t_eval.end,
            ODE_PARAMS.t_eval.step,
        ],
    ):
        """Class for solving Ordinary Differential equations for RPS simulation

        Args:
            Z_COPYCAT_RATE (float, optional): Copycat rate. Defaults to ODE_PARAMS["z"].
            MU_MUTATION_RATE (float, optional): Mutation rate. Defaults to ODE_PARAMS["mu"].
            initial_pop (dict[Card, int], optional): Initial card populations as counts of each type of card. Defaults to {}.
            t_interval(tuple[int,int]) : Time interval to solve ODE (start, finish)
            t_eval(list[int]) : Sample points for results reporting [start, end, step size]
        """

        self.z = Z_COPYCAT_RATE
        self.mu = MU_MUTATION_RATE
        self.initial_counts: dict[Card, int] = initial_counts
        self.d_rock = 0.0
        self.d_paper = 0.0
        self.d_scissors = 0.0
        self.initial_pop = [0.0] * 3
        self.t_interval = t_interval

        self.t_eval = t_eval
        self.t_eval = np.linspace(t_eval[0], t_eval[1], t_eval[2])

        self.convert_initial_pop_to_float()

    def convert_initial_pop_to_float(self):
        """Converts the integer card counts to float populations relative to the
        sum of all card counts.
        """
        card_counts = self.initial_counts

        N_rock = card_counts[Card.ROCK]
        N_paper = card_counts[Card.PAPER]
        N_scissors = card_counts[Card.SCISSOR]
        logger.debug(f"card counts :{[N_rock, N_paper, N_scissors]}")

        N_ALL_CARDS = N_rock + N_paper + N_scissors

        self.d_rock = N_rock / N_ALL_CARDS
        self.d_paper = N_paper / N_ALL_CARDS
        self.d_scissors = N_scissors / N_ALL_CARDS

        self.initial_pop = [self.d_rock, self.d_scissors, self.d_paper]
        logger.debug(f"Initial pops {self.initial_pop}")

    def diff_eqn_szolnoki(self, t: float, y: np.ndarray):
        """Modified RPS population density system of differential equations from Szolnoki et al (2014)

        Args:
            mu (float): Mutation rate (0.0-1.0)
            z (float): Copycat rate (0.0-1.0)
            d_rock (float): Initial pop density, rock
            d_paper (float): Initial pop density, paper
            d_scissors (float): Initial pop density, scissors
        """
        z = self.z
        mu = self.mu
        a, b, c = y

        dadt = a * (z * (b - c)) + mu * (b + c - 2 * a)
        dbdt = b * (z * (c - a)) + mu * (a + c - 2 * b)
        dcdt = c * (z * (a - b)) + mu * (a + b - 2 * c)

        return [dadt, dbdt, dcdt]

    def SolveODE(self) -> OdeResult:
        sol = solve_ivp(
            fun=self.diff_eqn_szolnoki,
            t_span=self.t_interval,
            y0=self.initial_pop,
            t_eval=self.t_eval,
        )

        return sol
