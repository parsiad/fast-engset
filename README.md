fast-engset
===========

MATLAB code to compute the blocking probability ```P``` in the Engset model:

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
