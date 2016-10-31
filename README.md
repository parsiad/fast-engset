fast-engset
===========

__Warning__: This is a legacy release (for MATLAB/GNU Octave users) that is now unmaintained. Please consider using the Python version (see https://github.com/parsiad/fast-engset/releases for the latest releases), which is actively maintained.

MATLAB/GNU Octave code to compute the blocking probability ```P``` in the Engset model:

```
                         m                              
         binom{N - 1}{m}A                            E        
P = --------------------------    where    A = -------------.
     __ m                    X                  N - E(1 - P)   
    \        binom{N - 1}{X}A                           
    /__ X = 0                                           
```

```N``` denotes the number of *sources*, ```m``` the number of *servers*, and ```E``` the *offered traffic* from __all__ sources. 

```E``` is usually given by ```E = lambda mu```, where ```lambda``` is the *arrival rate* of all sources and ```mu``` is the *mean service time* for a given request.

__Warning__: Certain texts use instead the __normalized__ offered traffic,  which is instead defined as ```E = lambda mu / N```.

```matlab
m = 5  % Number of servers
N = 10 % Number of sources
E = 2  % Total offered traffic from all sources

% Blocking probability
P = fast_engset(m, N, E)
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
