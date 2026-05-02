"""Wall-clock comparison of scipy.integrate.solve_ivp methods on the
modified Szolnoki RPS ODE. Justifies the choice of RK45 in the paper.

Run directly:
    python tests/test_ode_solver_timing.py

Or via pytest (prints timings, no assertions on speed):
    pytest tests/test_ode_solver_timing.py -s
"""

from __future__ import annotations

import time
from statistics import mean, stdev

import numpy as np
from scipy.integrate import solve_ivp

from cse6730_project.config import ODE_PARAMS
from cse6730_project.models import Card
from cse6730_project.ode.ode import OdeRPS
from cse6730_project.utils import logger


METHODS = ["RK45", "RK23", "DOP853", "Radau", "BDF", "LSODA"]
N_REPEATS = 25
RTOL = 1e-6
ATOL = 1e-9


def _build_ode() -> OdeRPS:
    initial_counts = {Card.ROCK: 3, Card.PAPER: 3, Card.SCISSOR: 3}
    return OdeRPS(
        Z_COPYCAT_RATE=ODE_PARAMS.z,
        MU_MUTATION_RATE=ODE_PARAMS.mu,
        initial_counts=initial_counts,
    )


def _time_method(ode: OdeRPS, method: str, n_repeats: int) -> dict:
    times: list[float] = []
    last_sol = None
    for _ in range(n_repeats):
        t0 = time.perf_counter()
        sol = solve_ivp(
            fun=ode.diff_eqn_szolnoki,
            t_span=ode.t_interval,
            y0=ode.initial_pop,
            t_eval=ode.t_eval,
            method=method,
            rtol=RTOL,
            atol=ATOL,
        )
        times.append(time.perf_counter() - t0)
        last_sol = sol

    return {
        "method": method,
        "mean_ms": mean(times) * 1e3,
        "stdev_ms": (stdev(times) * 1e3) if len(times) > 1 else 0.0,
        "min_ms": min(times) * 1e3,
        "nfev": last_sol.nfev,
        "njev": getattr(last_sol, "njev", 0),
        "nlu": getattr(last_sol, "nlu", 0),
        "success": last_sol.success,
        "final_y": np.asarray(last_sol.y[:, -1]),
    }


def run_benchmark() -> list[dict]:
    ode = _build_ode()
    # Warm-up to amortize import / JIT-style first-call costs.
    for m in METHODS:
        solve_ivp(
            fun=ode.diff_eqn_szolnoki,
            t_span=ode.t_interval,
            y0=ode.initial_pop,
            t_eval=ode.t_eval,
            method=m,
            rtol=RTOL,
            atol=ATOL,
        )

    results = [_time_method(ode, m, N_REPEATS) for m in METHODS]

    ref = next(r for r in results if r["method"] == "RK45")["final_y"]

    logger.info(
        "Szolnoki RPS ODE solver timings "
        "(t_span=%s, n_eval=%d, rtol=%g, atol=%g, repeats=%d)",
        ode.t_interval,
        len(ode.t_eval),
        RTOL,
        ATOL,
        N_REPEATS,
    )
    header = f"{'method':<8} {'mean (ms)':>10} {'std (ms)':>10} {'min (ms)':>10} {'nfev':>6} {'njev':>5} {'nlu':>5} {'max|Δy| vs RK45':>18}"
    logger.info(header)
    logger.info("-" * len(header))
    for r in results:
        diff = float(np.max(np.abs(r["final_y"] - ref)))
        logger.info(
            "%-8s %10.3f %10.3f %10.3f %6d %5d %5d %18.2e",
            r["method"],
            r["mean_ms"],
            r["stdev_ms"],
            r["min_ms"],
            r["nfev"],
            r["njev"],
            r["nlu"],
            diff,
        )
    return results


def test_solver_timing_smoke():
    """Smoke test: every method completes successfully on the model ODE."""
    results = run_benchmark()
    for r in results:
        assert r["success"], f"{r['method']} failed to integrate"


if __name__ == "__main__":
    run_benchmark()
