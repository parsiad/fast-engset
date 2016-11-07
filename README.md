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
@article {MR3503106,
    AUTHOR = {Azimzadeh, P. and Carpenter, T.},
     TITLE = {Fast {E}ngset computation},
   JOURNAL = {Oper. Res. Lett.},
  FJOURNAL = {Operations Research Letters},
    VOLUME = {44},
      YEAR = {2016},
    NUMBER = {3},
     PAGES = {313--318},
      ISSN = {0167-6377},
     CODEN = {ORLED5},
   MRCLASS = {90B22 (60K30)},
  MRNUMBER = {3503106},
MRREVIEWER = {Vyacheslav M. Abramov},
       DOI = {10.1016/j.orl.2016.02.011},
       URL = {http://dx.doi.org/10.1016/j.orl.2016.02.011},
}
```
