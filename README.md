# 🏃💨 fast-engset

**fast-engset** is a Python package providing fast and accurate routines to compute various quantities in the Engset model (detailed below).
It is released under an MIT License.

fast-engset uses Numba for JIT compilation and is tested against thousands of synthetic data points for validity.

## Table of contents

* [Citation](#📔-citation)
* [Installation](#💾-installation)
* [The Engset formula](#🧑‍🏫-the-engset-formula)
* [Tutorial](#🧑‍🏫-tutorial)
  * [Computing the blocking probability](#computing-the-blocking-probability)
  * [Computing the minimum number of servers required](#computing-the-minimum-number-of-servers-required)
  * [Computing the maximum number of sources serviceable](#computing-the-maximum-number-of-sources-serviceable)
  * [Computing the offered traffic](#computing-the-offered-traffic)
* [Advanced](#🦸-advanced)
  * [Specifying the algorithm](#specifying-the-algorithm)
  * [Specifying an initial guess](#specifying-an-initial-guess)
  * [Disabling JIT compilation](#disabling-jit-compilation)
  * [Disabling logging](#disabling-logging)
* [Timing results](#⌛-timing-results)
  * [JIT enabled](#jit-enabled)
  * [JIT disabled](#jit-disabled)

## 📔 Citation

If you use this in an academic or otherwise public work, **please cite the corresponding journal article**:

[Azimzadeh, Parsiad](https://parsiad.ca), and Tommy Carpenter. "Fast Engset computation." *Operations Research Letters* 44.3 (2016): 313-318. [\[arXiv\]](https://arxiv.org/abs/1511.00291) [\[bibtex\]](MR3503106.bib) [\[doi\]](https://doi.org/10.1016/j.orl.2016.02.011) [\[pdf\]](https://arxiv.org/pdf/1511.00291.pdf) [\[pypi\]](https://pypi.python.org/pypi/fast-engset/)

## 💾 Installation

```
pip install fast_engset
```

## 🧑‍🏫 The Engset formula

<img alt="Tore Olaus Engset" src="images/engset.jpg" style="border-radius: 25px; float: right; margin: 0 0 1em 1em;">

The [Engset formula](https://en.wikipedia.org/wiki/Engset_formula) describes the blocking probability of a particular type of (finite population) queue.

It is given by

![](images/formula.svg)

*P* is the **blocking probability**, *c* is the **number of servers** (a.k.a. lines), *N* is the **number of sources**, λ is the idle source arrival rate, and *h* is the average holding time.

In practice, λ is unknown (or hard to estimate) while α, the **offered traffic** per-source, is known.
In this case, the relationship

![](images/substitution.svg)

is substituted into the Engset formula.

After performing this substitution, the Engset formula allows us to solve for one of the four parameters *P*, *c*, *N*, or α given the other three.

However, doing so requires the use of numerical methods.
That's where fast-engset comes in.

## 🧑‍🏫 Tutorial

Let's start by importing the Python package.

```python
>>> import fast_engset as fe
```

### Computing the blocking probability

Suppose we have a queue with the following parameters:

```python
>>> n_servers          = 5    # c
>>> n_sources          = 10   # N
>>> per_source_traffic = 0.2  # α
```

To obtain the blocking probability of this queue, we use `fe.blocking_prob`:

```python
>>> total_traffic = n_sources * per_source_traffic
>>> result = fe.blocking_prob(n_servers, n_sources, total_traffic)
```

`result` is a [namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) which contains the blocking probability along with some additional information.
Namely, it also contains the number of iterations required by the underlying numerical algorithm before convergence and a status code indicating whether or not the method succeeded.

```python
>>> print(result)
_Result(n_iters=3, status=<Status.OK: 0>, value=0.016349962386312377)
```

If we are only interested in the blocking probability, we can extract that quantity alone from the namedtuple:

```python
>>> blocking_prob = result.value
>>> blocking_prob
0.016349962386312377
```

### Computing the minimum number of servers required

Suppose now that we have in mind a blocking probability *P* that we would like our queue to operate at.
However, we do not know how many servers are needed to achieve it.

For the sake of exposition, let's fix some parameters:

```python
>>> blocking_prob      = 0.017  # P
>>> n_sources          = 10     # N
>>> per_source_traffic = 0.2    # α
```

To obtain the minimum number of servers required to operate at a blocking probability of **at most** `blocking_prob`, we use `fe.n_servers`:

```python
>>> total_traffic = n_sources * per_source_traffic
>>> fe.n_servers(blocking_prob, n_sources, total_traffic)
_Result(n_iters=4, status=<Status.OK: 0>, value=5)
```

The number of servers required is 5.
Indeed, from the previous example, we know that the blocking probability of this arrangement is roughly 0.0163, which is smaller than our choice of *P* = 0.017.
On the other hand, if we had tried to "cut costs" and used only 4 servers...

```python
>>> n_servers = 4
>>> fe.blocking_prob(n_servers, n_sources, total_traffic)
_Result(n_iters=3, status=<Status.OK: 0>, value=0.06495282643260683)
```

...we would obtain a blocking probability of roughly 0.0650, which is larger than our choice of *P* = 0.017.

### Computing the maximum number of sources serviceable

As in the previous example, suppose we have in mind a blocking probability *P* that we would like our queue to operate at.
We would like to find out the maximum number of sources the queue can service.

For the sake of exposition, let's fix some parameters:

```python
>>> blocking_prob      = 0.017  # P
>>> n_servers          = 5      # c
>>> per_source_traffic = 0.2    # α
```

To obtain the maximum number of sources serviceable while operating at a blocking probability of **at most** `blocking_prob`, we use `fe.n_sources`:

```python
>>> total_traffic = n_sources * per_source_traffic
>>> fe.n_sources(blocking_prob, n_servers, total_traffic)
_Result(n_iters=7, status=<Status.OK: 0>, value=10)
```

It is possible, in certain cases, that the queue can support an infinite number of sources.
For example, consider a queue with a single server and a total traffic of 1 Erlang.
Such a queue has a blocking probability less than 1/2 for any finite number of sources.

`fe.n_sources` detects cases like the one described above and return a special status code:

```python
>>> fe.n_sources(blocking_prob=0.5, n_servers=1, total_traffic=1.0)
_Result(n_iters=23, status=<Status.UNBOUNDED: 1>, value=9223372036854775807)
```

As such, it is a good idea to check for the `fe.Status.UNBOUNDED` status code when using this function.

### Computing the offered traffic

Lastly, suppose we know the number of servers, sources, and desired blocking probability and want to determine the offered traffic.

For the sake of exposition, let's fix some parameters:

```python
>>> blocking_prob      = 0.017  # P
>>> n_servers          = 5      # c
>>> n_sources          = 10     # N
```

To obtain the total offered traffic from all sources, we use `fe.total_traffic`:

```python
>>> result = fe.total_traffic(blocking_prob, n_servers, n_sources)
>>> per_source_traffic = result.value / n_sources  # Convert back to α
>>> per_source_traffic
0.20198467001318932
```

Note that sufficiently large blocking probabilities are only achievable with a total traffic greater than the number of sources.
Depending on your application, this may not be physically meaningful.
`fe.total_traffic` issues a warning in this case:

```python
>>> fe.total_traffic(blocking_prob=0.75, n_servers=5, n_sources=10)
_Result(n_iters=31, status=<Status.OK: 0>, value=19.008517153561115)
```
```
fast-engset: [WARNING] Encountered total traffic greater than the number of
sources (while the Engset formula is still well-defined under this
parametrization, the physical meaning may be lost as each source is generally
assumed to offer at most one Erlang of traffic)
```

## 🦸 Advanced

### Specifying the algorithm

Some of the routines discussed in the [Tutorial](#🧑‍🏫-tutorial) support more than one numerical algorithm.
The table below summarizes support:

✅ **Supported**

⛔ Supported but **numerically unstable** in certain regions

|                  |`fe.Algorithm.BISECT`|`fe.Algorithm.FIXEDP`|`fe.Algorithm.NEWTON`|
|------------------|---------------------|---------------------|---------------------|
|`fe.blocking_prob`|✅                   |⛔                   |✅                   |
|`fe.n_servers`    |✅                   |                     |                     |
|`fe.n_sources`    |✅                   |                     |                     |
|`fe.total_traffic`|✅                   |                     |⛔                   |

The unstable combinations are available primarily for educational purposes.
By default, all routines default to `fe.Algorithm.BISECT` except for `fe.blocking_prob`, which defaults to `fe.Algorithm.NEWTON` due to its speed and stability.

You can specify an algorithm with the `alg` argument.
For example...

```python
>>> fe.blocking_prob(n_servers, n_sources, total_traffic,
...                  alg=fe.Algorithm.BISECT)
```

### Specifying an initial guess

When using either `fe.Algorithm.NEWTON` or `fe.Algorithm.FIXEDP`, it is possible to specify an initial guess to speed up convergence.
For example...

```python
>>> fe.blocking_prob(n_servers=5, n_sources=10, total_traffic=5.0,
...                  alg=fe.Algorithm.NEWTON)
_Result(n_iters=4, status=<Status.OK: 0>, value=0.24767800914641194)
>>> fe.blocking_prob(n_servers=5, n_sources=10, total_traffic=5.0,
...                  alg=fe.Algorithm.NEWTON, initial_guess=0.2)
_Result(n_iters=3, status=<Status.OK: 0>, value=0.24767800914641203)
```

### Disabling JIT compilation

Set the environment variable `FAST_ENGSET_NO_JIT` to disable JIT compilation.

This must be done before importing the package (e.g., importing the package and then setting `os.environ['FAST_ENGSET_NO_JIT'] = 1` has no effect).

### Disabling logging

```python
>>> import logging
>>> logging.getLogger('fast-engset').setLevel(logging.CRITICAL)
```

## ⌛ Timing results

Timing tests were run on an AMD FX(tm)-6300 Six-Core Processor.
There is **roughly an order of magnitude improvement with JIT compilation enabled**.

### JIT enabled

```python
>>> %timeit fe.blocking_prob(5, 10, 2.0)
7.98 µs ± 66.3 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

>>> %timeit fe.n_servers(0.017, 10, 2.0)
6.73 µs ± 29.9 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

>>> %timeit fe.n_sources(0.017, 5, 2.0)
7.28 µs ± 41.9 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

>>> %timeit fe.total_traffic(0.017, 5, 10)
8.15 µs ± 40.9 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

### JIT disabled

```python
>>> %timeit fe.blocking_prob(5, 10, 2.0)
59.6 µs ± 405 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

>>> %timeit fe.n_servers(0.017, 10, 2.0)
37.9 µs ± 740 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

>>> %timeit fe.n_sources(0.017, 5, 2.0)
87.8 µs ± 520 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

>>> %timeit fe.total_traffic(0.017, 5, 10)
209 µs ± 595 ns per loop (mean ± std. dev. of 7 runs, 1000 loops each)
```
