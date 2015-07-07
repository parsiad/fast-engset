#!/usr/bin/env python

"""
The MIT License (MIT)

Copyright (c) 2015 Parsiad Azimsadeh and Tommy Carpenter>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.
"""

"""
Computes the blocking probability of a finite population queue.


Example usage:

import fast_engset as fe

m = 5  # Number of servers
N = 10 # Number of sources
E = 2  # Total offered traffic from all sources

# Blocking probability
P = fe.compute(m, N, E)
"""

def compute(m, N, E, tol=1e-6):
    """ Computes the blocking probability of a finite population queue as given
    by the Engset formula.

    m       -- number of servers (a nonnegative integer).
    N       -- number of sources (a nonnegative integer).
    E       -- offered traffic from all sources (a positive number) given by
               E = lambda * mu, where lambda is the arrival rate of requests and
               mu is the mean service time.
    tol     -- Error tolerance (default 1e-6).
    """

    # Error checking
    if m < 0 or m % 1 != 0:
        raise ValueError('The number of servers must be a nonnegative integer.')

    if N < 0 or N % 1 != 0:
        raise ValueError('The number of sources must be a nonnegative integer.')

    if E <= 0:
        raise ValueError('The offered traffic must be a positive number.')

    # Trivial cases
    if N <= m: return 0
    if m == 0: return 1

    return __quasi_newton(m, N, E, tol=tol)

################################################################################

def __quasi_newton(m, N, E, tol=pow(2,-24), P=0.5, n_max=1024, verbose=False):
    """ Computes the blocking probability of a finite population queue as given
    by the Engset formula using a quasi-Newton's method.

    If the iteration does not converge, None is returned.

    m       -- number of servers.
    N       -- number of sources.
    E       -- offered traffic from all sources given by E = lambda * mu, where
               lambda is the arrival rate of requests and mu is the mean service
               time.
    tol     -- error tolerance (default 2^-24).
    P       -- initial guess for the blocking probability (default 0.5).
    n_max   -- max number of iterations before giving up (default 1024).
    verbose -- if True, a tuple (P, n) is returned where P is the blocking
               probability and n is the number of iterations that were required;
               otherwise, only P is returned (default False).
    """

    # Precompute coefficients of 1/f(P) = hyp2f1(1, -m, N-m, 1-N/E-P)
    f = m
    g = N-m
    c = [0]*(m+1)
    c[0] = 1.
    k = 1
    while True:
        c[k] = f/g * c[k-1]
        f -= 1
        if f == 0: break
        k += 1
        g += 1

    y = N/E-1
    for n in range(1, n_max+1):
        # Compute f(P) and f(P + dP)
        x    = P+y
        h1   = 1.
        h1e  = 1.
        mlt  = x
        mlte = x+tol
        k = 1
        while True:
            u  = c[k] * mlt
            ue = c[k] * mlte
            h1  += u
            h1e += ue
            if k == m or (abs(u/h1) <= tol and abs(ue/h1e) <= tol): break
            k += 1
            mlt  *= x
            mlte *= x+tol

        # Newton iteration
        recip = 1/h1
        P_new = P + (recip - P)/( (recip - 1/h1e)/tol + 1 )

        if abs(P - P_new) <= tol:
            if verbose: return (P_new, n)
            return P_new

        P = P_new

    return None

def __newton(m, N, E, tol=pow(2,-24), P=0.5, n_max=1024, verbose=False):
    """ Computes the blocking probability of a finite population queue as given
    by the Engset formula using Newton's method.

    For a list of parameters, see fast_engset.quasi_newton.
    """

    from scipy.special import hyp2f1

    b = -m
    c = N-m
    d = 1-N/E

    for n in range(1, n_max+1):
        h1 = hyp2f1(1, b  , c  , d-P)
        h2 = hyp2f1(2, b+1, c+1, d-P)

        P_new = P + ( 1/h1 - P )/( m/c * h2/(h1*h1) + 1 )

        if abs(P - P_new) <= tol:
            if verbose: return (P_new, n)
            return P_new

        P = P_new

    return None

def __bisect(m, N, E, tol=pow(2,-24), n_max=1024, verbose=False):
    """ Computes the blocking probability of a finite population queue as given
    by the Engset formula using bisection.

    For a list of parameters, see fast_engset.quasi_newton.
    """

    from scipy.special import hyp2f1

    b = -m
    c = N-m
    d = 1-N/E

    lo = 0
    hi = 1
    for n in range(1, n_max+1):
        P = (lo + hi) / 2

        if (hi - lo)/2 <= tol:
            if verbose: return (P, n)
            return P

        if 1/hyp2f1(1, b, c, d-P) < P: hi = P
        else:                          lo = P

def __fixed_point(m, N, E, tol=pow(2,-24), P=0.5, n_max=1024, verbose=False):
    """ Computes the blocking probability of a finite population queue as given
    by the Engset formula using a fixed point iteration.

    For a list of parameters, see fast_engset.quasi_newton.
    """

    from scipy.special import hyp2f1

    b = -m
    c = N-m
    d = 1-N/E

    for n in range(1, n_max+1):
        P_new = 1/hyp2f1(1, b, c, d-P)

        if abs(P - P_new) <= tol:
            if verbose: return (P_new, n)
            return P_new

        P = P_new

