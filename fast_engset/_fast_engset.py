"""_fast_engset.py"""

from typing import Any, NamedTuple, Union
from enum import Enum
import logging
import math
import os
import sys

from numpy.typing import NDArray
import numpy as np

_TOTAL_TRAFFIC_WARNING = (
    "Encountered total traffic greater than the number of sources (while the Engset formula is "
    "still well-defined under this parametrization, the physical meaning may be lost as each "
    "source is generally assumed to offer at most one Erlang of traffic)"
)


def _maybe_jit(func):
    return func


logger = logging.getLogger("fast-engset")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(name)s: [%(levelname)s] %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


if "FAST_ENGSET_NO_JIT" not in os.environ:
    try:
        from numba import jit  # type: ignore

        _maybe_jit = jit(nopython=True)
    except ImportError:
        logging.getLogger("fast-engset").warning("Unable to JIT due to missing Numba")


class Status(Enum):
    """Status codes."""

    OK = 0
    UNBOUNDED = 1
    MAX_N_ITERS_REACHED = -1
    UNSTABLE = -2


class _Result(NamedTuple):
    """Computation result."""

    n_iters: int
    status: Status
    value: Union[float, int]


class Algorithm(Enum):
    """Algorithm to use for computing blocking probability."""

    BISECT = 0
    FIXEDP = 1
    NEWTON = 2


def blocking_prob(
    n_servers: int,
    n_sources: int,
    total_traffic: float,
    alg: Algorithm = Algorithm.NEWTON,
    max_n_iters: int = 1024,
    tol: float = pow(2, -24),
    check: bool = True,
    **kwargs: Any,
) -> _Result:
    """Blocking probability in the Engset model.

    Parameters
    ----------
    n_servers
        Number of servers.
    n_sources
        Number of sources.
    total_traffic
        Total offered traffic from all sources in Erlangs. Satisfies ``total_traffic = n_sources * per_source_traffic``
        where ``per_source_traffic`` is the offered traffic per-source.
    alg
        One of ``Algorithm.BISECT``, ``Algorithm.FIXEDP``, ``Algorithm.NEWTON``. The fixed point algorithm can be
        unstable; use at your own risk.
    max_n_iters
        Maximum number of iterations.
    tol
        Error tolerance.
    check
        Whether to validate arguments.
    initial_guess
        Initial guess (suported only by ``Algorithm.FIXEDP`` and ``Algorithm.NEWTON``).

    Returns
    -------
    n_iters
        Number of iterations required to converge.
    status
        Describes if the method succeeded and if not, how it failed.
    value
        Result of the computation.
    """
    if check:
        _validate_args(
            blocking_prob_=0.5,
            n_servers_=n_servers,
            n_sources_=n_sources,
            total_traffic_=total_traffic,
        )
    n_servers = int(n_servers)
    n_sources = int(n_sources)

    if alg == Algorithm.BISECT:
        func = _blocking_prob_bisect
    elif alg == Algorithm.FIXEDP:
        logging.getLogger("fast-engset").warning(
            "The fixed point method for the blocking probability can be unstable; use at your own risk"
        )
        func = _blocking_prob_fixed_point
    elif alg == Algorithm.NEWTON:
        func = _blocking_prob_newton
    else:
        raise ValueError("Unsupported algorithm")

    return func(n_servers, n_sources, total_traffic, max_n_iters, tol, **kwargs)


def n_servers(
    blocking_prob: float,
    n_sources: int,
    total_traffic: int,
    alg: Algorithm = Algorithm.BISECT,
    max_n_iters: int = 1024,
    tol: float = pow(2, -24),
    check: bool = True,
    **kwargs: Any,
) -> _Result:
    """Minimum number of servers required for the queue to operate below a given blocking probability.

    Parameters
    ----------
    blocking_prob
        Blocking probability.
    n_sources
        Number of sources.
    total_traffic
        Total offered traffic from all sources in Erlangs. Satisfies ``total_traffic = n_sources * per_source_traffic``
        where ``per_source_traffic`` is the offered traffic per-source.
    alg
        Accepts only ``Algorithm.BISECT``.
    max_n_iters
        Maximum number of iterations.
    tol
        Error tolerance.
    check
        Whether to validate arguments.

    Returns
    -------
    n_iters
        Number of iterations required to converge.
    status
        Describes if the method succeeded and if not, how it failed.
    value
        Result of the computation.
    """
    if check:
        _validate_args(
            blocking_prob_=blocking_prob,
            n_servers_=1,
            n_sources_=n_sources,
            total_traffic_=total_traffic,
        )
    n_sources = int(n_sources)

    if alg == Algorithm.BISECT:
        func = _n_servers_bisect
    else:
        raise ValueError("Unsupported algorithm")

    return func(blocking_prob, n_sources, total_traffic, max_n_iters, tol, **kwargs)


def n_sources(
    blocking_prob: float,
    n_servers: int,
    total_traffic: float,
    alg: Algorithm = Algorithm.BISECT,
    max_n_iters: int = 1024,
    tol: float = pow(2, -24),
    check: bool = True,
    **kwargs: Any,
) -> _Result:
    """Maximum number of sources serviceable while remaining below a given blocking probability.

    Some parametrizations may support an infinite number of sources without exceeding the specified blocking
    probability. For example, consider a queue with a single server and a total traffic of 1 Erlang. It is fairly
    straightforward to show that the blocking probability tends to 1/2 as the number of servers grow unbounded. In such
    cases, this routine will return a status code of ``Status.UNBOUNDED`` and a value equal to ``sys.maxsize`` (a large,
    arbitrary integer).

    Parameters
    ----------
    blocking_prob
        Blocking probability.
    n_servers
        Number of servers.
    total_traffic
        Total offered traffic from all sources in Erlangs. Satisfies ``total_traffic = n_sources * per_source_traffic``
        where ``per_source_traffic`` is the offered traffic per-source.
    alg
        Accepts only ``Algorithm.BISECT``.
    max_n_iters
        Maximum number of iterations.
    tol
        Error tolerance.
    check
        Whether to validate arguments.

    Returns
    -------
    n_iters
        Number of iterations required to converge.
    status
        Describes if the method succeeded and if not, how it failed.
    value
        Result of the computation.
    """
    if check:
        _validate_args(
            blocking_prob_=blocking_prob,
            n_servers_=n_servers,
            n_sources_=sys.maxsize,
            total_traffic_=total_traffic,
        )
    n_servers = int(n_servers)

    if alg == Algorithm.BISECT:
        func = _n_sources_bisect
    else:
        raise ValueError("Unsupported algorithm")

    return func(blocking_prob, n_servers, total_traffic, max_n_iters, tol, **kwargs)


def total_traffic(
    blocking_prob: float,
    n_servers: int,
    n_sources: int,
    alg: Algorithm = Algorithm.BISECT,
    max_n_iters: int = 1024,
    tol: float = pow(2, -24),
    check: bool = True,
    **kwargs: Any,
) -> _Result:
    """Total offered traffic in the Engset model.

    Note that for sufficiently large blocking probabilities are only achievable with a total traffic greater than the
    number of servers. Depending on your application, this may not be physically meaningful. `fe.total_traffic` issues
    a warning in this case:

    Parameters
    ----------
    blocking_prob
        Blocking probability.
    n_servers
        Number of servers.
    n_sources
        Number of sources.
    alg
        One of ``Algorithm.BISECT``, ``Algorithm.NEWTON``. The Newton's method can be unstable; use at your own risk.
    max_n_iters
        Maximum number of iterations.
    tol
        Error tolerance.
    check
        Whether to validate arguments.
    initial_guess
        Initial guess (suported only by ``Algorithm.NEWTON``).

    Returns
    -------
    n_iters
        Number of iterations required to converge.
    status
        Describes if the method succeeded and if not, how it failed.
    value
        Result of the computation.
    """
    if check:
        _validate_args(
            blocking_prob_=blocking_prob,
            n_servers_=n_servers,
            n_sources_=n_sources,
            total_traffic_=1.0,
        )
    n_servers = int(n_servers)
    n_sources = int(n_sources)

    if alg == Algorithm.BISECT:
        func = _total_traffic_bisect
    elif alg == Algorithm.NEWTON:
        logging.getLogger("fast-engset").warning(
            "Newton's method for the total traffic can be unstable; use at your own risk"
        )
        func = _total_traffic_newton
    else:
        raise ValueError("Unsupported algorithm")

    result = func(blocking_prob, n_servers, n_sources, max_n_iters, tol, **kwargs)
    if result.status == Status.OK and result.value > n_sources:
        logging.getLogger("fast-engset").warning(_TOTAL_TRAFFIC_WARNING)
    return result


@_maybe_jit
def _hyp2f1_coefs(
    param1: int,
    param2: int,
) -> NDArray[np.float64]:
    """Coefficients of ``f(z) = hyp2f1(1, -param1, param2 - param1, z)``."""
    f = param1
    g = param2 - param1
    coefs = np.zeros((param1 + 1,))
    coefs[0] = 1.0
    k = 1
    while True:
        coefs[k] = f / g * coefs[k - 1]
        f -= 1
        if f == 0:
            break
        k += 1
        g += 1
    return coefs


@_maybe_jit
def _hyp2f1_from_coefs(
    coefs: NDArray[np.float64],
    param1: int,
    arg: float,
    tol: float,
) -> float:
    """Computes ``hyp2f1(1, -param1, param2 - param1, -arg)`` using the output from ``_hyp2f1_coefs``."""
    h1 = 1.0
    mlt = arg
    k = 1
    while True:
        u = coefs[k] * mlt
        h1 += u
        if k == param1 or abs(u / h1) <= tol:
            break
        k += 1
        mlt *= arg
    return h1


@_maybe_jit
def _hyp2f1(
    param1: int,
    param2: int,
    arg: float,
    tol: float,
) -> float:
    coefs = _hyp2f1_coefs(param1, param2)
    return _hyp2f1_from_coefs(coefs, param1, arg, tol)


@_maybe_jit
def _blocking_prob_newton(
    n_servers_: int,
    n_sources_: int,
    total_traffic_: float,
    max_n_iters: int,
    tol: float,
    initial_guess: float = 0.5,
) -> _Result:
    coefs = _hyp2f1_coefs(n_servers_, n_sources_)
    y = n_sources_ / total_traffic_ - 1.0
    blocking_prob_ = initial_guess
    for n_iters in range(1, max_n_iters + 1):
        x = blocking_prob_ + y
        f = 1.0 / _hyp2f1_from_coefs(coefs, n_servers_, x, tol)
        g = 1.0 / _hyp2f1_from_coefs(coefs, n_servers_, x + tol, tol)
        blocking_prob_new = blocking_prob_ + (f - blocking_prob_) / ((f - g) / tol + 1.0)
        if abs(blocking_prob_ - blocking_prob_new) <= tol:
            return _Result(n_iters=n_iters, status=Status.OK, value=blocking_prob_new)
        blocking_prob_ = blocking_prob_new
    return _Result(n_iters=max_n_iters, status=Status.MAX_N_ITERS_REACHED, value=blocking_prob_)


@_maybe_jit
def _blocking_prob_bisect(
    n_servers_: int,
    n_sources_: int,
    total_traffic_: float,
    max_n_iters: int,
    tol: float,
) -> _Result:
    coefs = _hyp2f1_coefs(n_servers_, n_sources_)
    y = n_sources_ / total_traffic_ - 1.0
    lo = 0.0
    hi = 1.0
    for n_iters in range(1, max_n_iters + 1):
        blocking_prob_ = (lo + hi) / 2.0
        if (hi - lo) / 2.0 <= tol:
            return _Result(n_iters=n_iters, status=Status.OK, value=blocking_prob_)
        if 1.0 / _hyp2f1_from_coefs(coefs, n_servers_, blocking_prob_ + y, tol) < blocking_prob_:
            hi = blocking_prob_
        else:
            lo = blocking_prob_
    return _Result(n_iters=max_n_iters, status=Status.MAX_N_ITERS_REACHED, value=blocking_prob_)


@_maybe_jit
def _blocking_prob_fixed_point(
    n_servers_: int,
    n_sources_: int,
    total_traffic_: float,
    max_n_iters: int,
    tol: float,
    initial_guess: float = 0.5,
) -> _Result:
    coefs = _hyp2f1_coefs(n_servers_, n_sources_)
    y = n_sources_ / total_traffic_ - 1.0
    blocking_prob_ = initial_guess
    for n_iters in range(1, max_n_iters + 1):
        blocking_prob_new = 1.0 / _hyp2f1_from_coefs(coefs, n_servers_, blocking_prob_ + y, tol)
        if abs(blocking_prob_ - blocking_prob_new) <= tol:
            return _Result(n_iters=n_iters, status=Status.OK, value=blocking_prob_new)
        blocking_prob_ = blocking_prob_new
    return _Result(n_iters=max_n_iters, status=Status.MAX_N_ITERS_REACHED, value=blocking_prob_)


@_maybe_jit
def _n_servers_bisect(
    blocking_prob_: float,
    n_sources_: int,
    total_traffic_: float,
    max_n_iters: int,
    tol: float,
) -> _Result:
    y = blocking_prob_ + n_sources_ / total_traffic_ - 1.0
    lo = 1
    hi = n_sources_
    for n_iters in range(1, max_n_iters + 1):
        if lo == hi:
            return _Result(n_iters=n_iters, status=Status.OK, value=lo)
        n_servers_ = (lo + hi) // 2
        if 1.0 / _hyp2f1(n_servers_, n_sources_, y, tol) < blocking_prob_:
            hi = n_servers_
        else:
            lo = n_servers_ + 1
    return _Result(n_iters=max_n_iters, status=Status.MAX_N_ITERS_REACHED, value=n_servers_)


@_maybe_jit
def _n_sources_bisect(
    blocking_prob_: float,
    n_servers_: int,
    total_traffic_: float,
    max_n_iters: int,
    tol: float,
) -> _Result:
    y = blocking_prob_ - 1.0
    lo = n_servers_
    hi = lo * 2

    n_pre_iters = 0
    prev = np.nan
    while True:
        n_pre_iters += 1
        value = 1.0 / _hyp2f1(n_servers_, hi, y + hi / total_traffic_, tol)
        if value >= blocking_prob_:
            break
        if abs(value - prev) <= abs(value) * tol:
            return _Result(n_iters=n_pre_iters, status=Status.UNBOUNDED, value=sys.maxsize)
        prev = value
        hi *= 2

    for n_iters in range(n_pre_iters + 1, max_n_iters + 1):
        if lo == hi:
            return _Result(n_iters=n_iters, status=Status.OK, value=lo)
        n_sources_ = math.ceil((lo + hi) / 2)
        if 1.0 / _hyp2f1(n_servers_, n_sources_, y + n_sources_ / total_traffic_, tol) < blocking_prob_:
            lo = n_sources_
        else:
            hi = n_sources_ - 1
    return _Result(n_iters=max_n_iters, status=Status.MAX_N_ITERS_REACHED, value=n_sources_)


@_maybe_jit
def _total_traffic_bisect(
    blocking_prob_: float,
    n_servers_: int,
    n_sources_: int,
    max_n_iters: int,
    tol: float,
) -> _Result:
    coefs = _hyp2f1_coefs(n_servers_, n_sources_)
    y = blocking_prob_ - 1.0
    lo = 0.0
    hi = float(n_sources_)

    n_pre_iters = 0
    while True:
        n_pre_iters += 1
        if 1.0 / _hyp2f1_from_coefs(coefs, n_servers_, y + n_sources_ / hi, tol) >= blocking_prob_:
            break
        hi *= 2.0

    for n_iters in range(n_pre_iters + 1, max_n_iters + 1):
        total_traffic_ = (lo + hi) / 2.0
        if (hi - lo) / 2.0 <= tol:
            return _Result(n_iters=n_iters, status=Status.OK, value=total_traffic_)
        if 1.0 / _hyp2f1_from_coefs(coefs, n_servers_, y + n_sources_ / total_traffic_, tol) < blocking_prob_:
            lo = total_traffic_
        else:
            hi = total_traffic_
    return _Result(n_iters=max_n_iters, status=Status.MAX_N_ITERS_REACHED, value=total_traffic_)


@_maybe_jit
def _total_traffic_newton(
    blocking_prob_: float,
    n_servers_: int,
    n_sources_: int,
    max_n_iters: int,
    tol: float,
    initial_guess: float = 1.0,
) -> _Result:
    coefs = _hyp2f1_coefs(n_servers_, n_sources_)
    y = blocking_prob_ - 1.0
    total_traffic_ = initial_guess
    for n_iters in range(1, max_n_iters + 1):
        h = total_traffic_ * tol
        f = 1.0 / _hyp2f1_from_coefs(coefs, n_servers_, y + n_sources_ / total_traffic_, tol)
        g = 1.0 / _hyp2f1_from_coefs(coefs, n_servers_, y + n_sources_ / (total_traffic_ + h), tol)
        dtotal_traffic = (f - g) / h
        if dtotal_traffic == 0.0:
            return _Result(n_iters=n_iters, status=Status.UNSTABLE, value=total_traffic_)
        total_traffic_new = total_traffic_ + (f - blocking_prob_) / dtotal_traffic
        if abs(total_traffic_ - total_traffic_new) / abs(total_traffic_new) <= tol:
            return _Result(n_iters=n_iters, status=Status.OK, value=total_traffic_new)
        total_traffic_ = total_traffic_new
    return _Result(n_iters=max_n_iters, status=Status.MAX_N_ITERS_REACHED, value=total_traffic_)


def _validate_args(
    blocking_prob_: float,
    n_servers_: int,
    n_sources_: int,
    total_traffic_: float,
) -> None:
    if blocking_prob_ <= 0.0 or blocking_prob_ >= 1.0:
        raise ValueError(f"Expected blocking_prob={blocking_prob_} to be strictly between 0 and 1")
    if n_servers_ <= 0 or n_servers_ % 1 != 0:
        raise ValueError(f"Expected n_servers={n_servers_} to be a positive integer")
    if n_sources_ <= n_servers_ or n_sources_ % 1 != 0:
        raise ValueError(f"Expected n_sources={n_sources_} to be an integer greater than {n_servers_}")
    if total_traffic_ <= 0.0:
        raise ValueError(f"Expected total_traffic={total_traffic_} to be positive")
    if total_traffic_ > n_sources_:
        logging.getLogger("fast-engset").warning(_TOTAL_TRAFFIC_WARNING)
