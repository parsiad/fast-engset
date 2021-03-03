"""test_fast_engset.py"""

# pylint: disable=missing-function-docstring
# pylint: disable=import-error

import numpy as np
import pytest

import fast_engset as fe


def rand_params_list(n_params=1000, max_n_sources=100, min_blocking_prob=1e-6):
    params_list = []
    while len(params_list) < n_params:
        n_sources = np.random.randint(low=2, high=max_n_sources)
        n_servers = np.random.randint(low=1, high=n_sources)
        total_traffic = np.random.uniform(low=0., high=n_servers)
        result = fe.blocking_prob(n_servers, n_sources, total_traffic)
        blocking_prob = result.value
        if result.status != fe.Status.OK or blocking_prob < min_blocking_prob:
            continue
        params = (blocking_prob, n_servers, n_sources, total_traffic)
        params_list.append(params)
    return params_list


@pytest.mark.parametrize(
    'n_servers,n_sources,total_traffic',
    [
        # yapf: disable
        (0, 1, 1.0),
        (1, 1, 1.0),
        (1, 2, 0.0),
        # yapf: enable
    ])
def test_bad_inputs_in_blocking_prob(n_servers, n_sources, total_traffic):
    with pytest.raises(ValueError):
        fe.blocking_prob(n_servers, n_sources, total_traffic)


@pytest.mark.parametrize(
    'blocking_prob,n_sources,total_traffic',
    [
        # yapf: disable
        (0.0, 2, 1.0),
        (1.0, 2, 1.0),
        (0.5, 1, 1.0),
        (0.5, 2, 0.0),
        # yapf: enable
    ])
def test_bad_inputs_in_n_servers(blocking_prob, n_sources, total_traffic):
    with pytest.raises(ValueError):
        fe.n_servers(blocking_prob, n_sources, total_traffic)


@pytest.mark.parametrize(
    'blocking_prob,n_servers,total_traffic',
    [
        # yapf: disable
        (0.0, 1, 1.0),
        (1.0, 1, 1.0),
        (0.5, 0, 1.0),
        (0.5, 1, 0.0),
        # yapf: enable
    ])
def test_bad_inputs_in_n_sources(blocking_prob, n_servers, total_traffic):
    with pytest.raises(ValueError):
        fe.n_sources(blocking_prob, n_servers, total_traffic)


@pytest.mark.parametrize(
    'blocking_prob,n_servers,n_sources',
    [
        # yapf: disable
        (0.0, 1, 2),
        (1.0, 1, 2),
        (0.5, 0, 2),
        (0.5, 1, 1),
        # yapf: enable
    ])
def test_bad_inputs_in_total_traffic(blocking_prob, n_servers, n_sources):
    with pytest.raises(ValueError):
        fe.total_traffic(blocking_prob, n_servers, n_sources)


# Reference values from https://www.erlang.com/calculator/engset/
@pytest.mark.parametrize(
    'blocking_prob,n_servers,n_sources,total_traffic',
    [
        # yapf: disable
        (0.016, 5, 10, 2.0),
        (0.181, 5, 20, 4.0),
        (0.471, 5, 20, 8.0),
        (0.709, 5, 20, 16.0),
        (0.764, 5, 40, 20.0),
        # yapf: enable
    ])
def test_blocking_prob(blocking_prob, n_servers, n_sources, total_traffic):
    max_n_iters = 1024

    result_bisect = fe.blocking_prob(n_servers,
                                     n_sources,
                                     total_traffic,
                                     alg=fe.Algorithm.NEWTON,
                                     max_n_iters=max_n_iters)
    result_newton = fe.blocking_prob(n_servers,
                                     n_sources,
                                     total_traffic,
                                     alg=fe.Algorithm.BISECT,
                                     max_n_iters=max_n_iters)
    result_fixedp = fe.blocking_prob(n_servers,
                                     n_sources,
                                     total_traffic,
                                     alg=fe.Algorithm.FIXEDP,
                                     max_n_iters=max_n_iters)

    assert result_bisect.n_iters <= max_n_iters
    assert result_fixedp.n_iters <= max_n_iters
    assert result_newton.n_iters <= max_n_iters

    assert result_bisect.status == fe.Status.OK
    assert result_fixedp.status == fe.Status.OK
    assert result_newton.status == fe.Status.OK

    assert pytest.approx(result_bisect.value, abs=1e-3) == blocking_prob
    assert pytest.approx(result_bisect.value) == result_fixedp.value
    assert pytest.approx(result_bisect.value) == result_newton.value


@pytest.mark.parametrize('blocking_prob,n_servers,n_sources,total_traffic', rand_params_list())
def test_n_servers(blocking_prob, n_servers, n_sources, total_traffic):
    max_n_iters = 1024

    result = fe.n_servers(blocking_prob - 1e-12, n_sources, total_traffic, max_n_iters=max_n_iters)
    assert result.n_iters <= max_n_iters
    assert result.status == fe.Status.OK
    assert result.value == n_servers + 1

    result = fe.n_servers(blocking_prob + 1e-12, n_sources, total_traffic, max_n_iters=max_n_iters)
    assert result.n_iters <= max_n_iters
    assert result.status == fe.Status.OK
    assert result.value == n_servers


@pytest.mark.parametrize('blocking_prob,n_servers,n_sources,total_traffic', rand_params_list())
def test_n_sources(blocking_prob, n_servers, n_sources, total_traffic):
    max_n_iters = 1024

    result = fe.n_sources(blocking_prob - 1e-12, n_servers, total_traffic, max_n_iters=max_n_iters)
    assert result.n_iters <= max_n_iters
    assert result.status == fe.Status.OK
    assert result.value == n_sources - 1

    result = fe.n_sources(blocking_prob + 1e-12, n_servers, total_traffic, max_n_iters=max_n_iters)
    assert result.n_iters <= max_n_iters
    assert result.status == fe.Status.OK
    assert result.value == n_sources


@pytest.mark.parametrize('blocking_prob,n_servers,n_sources,total_traffic', rand_params_list())
def test_total_traffic(blocking_prob, n_servers, n_sources, total_traffic):
    max_n_iters = 1024

    result_bisect = fe.total_traffic(blocking_prob, n_servers, n_sources, max_n_iters=max_n_iters)
    assert result_bisect.n_iters <= max_n_iters
    assert result_bisect.status == fe.Status.OK
    assert pytest.approx(result_bisect.value, abs=1e-6) == total_traffic
