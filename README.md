fast-engset
===========

Python code to compute the blocking probability ```P``` in the Engset model:

```
                         m
         binom{N - 1}{m}M                            E/N
P = --------------------------    where    M = ---------------.
     __ m                    X                  1 - E/N(1 - P)
    \        binom{N - 1}{X}M
    /__ X = 0
```

```N``` denotes the number of *sources*, ```m``` the number of *servers*, and ```E``` the *offered traffic* from __all__ sources.

```E``` is the *total offered traffic* given by ```E = N * alpha```, where ```alpha``` is the *offered traffic per-source*.

Installation
=======
`pip install fast_engset`

Example
=======

```python
from fast_engset import fe

m     = 5          # Number of servers
N     = 10         # Number of sources
alpha = 0.2        # Offered traffic from a SINGLE source
E     = N * alpha  # Total offered traffic from ALL sources

# Blocking probability
P = fe.compute(m, N, E)
```

Citation
========

If you are using this in an academic work, please cite the corresponding paper:

```
@article{azimzadeh2015fast,
  title={Fast Engset computation},
  author={Azimzadeh, Parsiad and Carpenter, Tommy},
  journal={Operations Research Letters},
  volume={44},
  number={3},
  pages={313--318},
  year={2016},
  issn={0167-6377},
  doi={10.1016/j.orl.2016.02.011},
  url={http://dx.doi.org/10.1016/j.orl.2016.02.011}
}
```
