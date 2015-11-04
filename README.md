fast-engset
===========

Python code to compute the blocking probability ```P``` in the Engset model:

```
                         m                              
         binom{N - 1}{m}M                            1        
P = --------------------------    where    M = ---------------.
     __ m                    X                  1 - E/N(1 - P)   
    \        binom{N - 1}{X}M                           
    /__ X = 0                                           
```

```N``` denotes the number of *sources*, ```m``` the number of *servers*, and ```E``` the *offered traffic* from __all__ sources. 

```E``` is given by ```E = N * lambda / mu```, where ```lambda``` is the *arrival rate* of a source and ```1/mu``` is the *mean service time* for a given request.

__Warning__: Don't forget to convert to the appropriate units! Certain texts use instead the __per-source__ offered traffic,  which is instead defined as ```alpha = E / N = lambda / mu```.

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
  journal={arXiv preprint arXiv:1511.00291},
  year={2015},
  url={http://arxiv.org/pdf/1511.00291.pdf}
}
```
