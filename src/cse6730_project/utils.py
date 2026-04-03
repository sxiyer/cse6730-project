from constants import RNG_SEED

import logging
import random
import numpy as np


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s"
)

logger = logging.getLogger("RPS_SIM")

rng_rand = random.Random(RNG_SEED)
rng_np = np.random.default_rng(seed = RNG_SEED)