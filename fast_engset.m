function P = fast_engset(m, N, E, tol, P, n_max)
% FAST_ENGSET Computes the blocking probability of a finite population queue.
%
%    If the iteration does not converge, -1 is returned.
%
%    m       -- number of servers.
%    N       -- number of sources.
%    E       -- offered traffic from all sources given by E = lambda * mu, where
%               lambda is the arrival rate of requests and mu is the mean
%               service time.
%    tol     -- error tolerance (default 1e-6).
%    P       -- initial guess for the blocking probability (default 0.5).
%    n_max   -- max number of iterations before giving up (default 1024).

    % Error checking
    if nargin < 3 || nargin > 6
        error('Wrong number of arguments.')
    end

    if m < 0 || rem(m, 1) ~= 0
        error('The number of servers must be a nonnegative integer.')
    end

    if N < 0 || rem(N, 1) ~= 0
        error('The number of sources must be a nonnegative integer.')
    end

    if E <= 0
        error('The offered traffic must be a positive number.')
    end

    % Trivial cases
    if N <= m; P = 0; return; end
    if m == 0; P = 1; return; end

    % Default arguments
    if nargin < 4; tol   = 1e-6; end
    if nargin < 5; P     =  0.5; end
    if nargin < 6; n_max = 1024; end

    % Precompute coefficients of 1/f(P) = hyp2f1(1, -m, N-m, 1-N/E-P)
    f = m;
    g = N-m;
    c = zeros(m,1);
    c(1) = f/g;
    for k = 2:m
        f = f-1;
        g = g+1;
        c(k) = f/g * c(k-1);
    end

    y = N/E-1;
    for n = 1:(n_max+1)
        % Compute f(P) and f(P + dP)
        x    = P+y;
        h1   = 1.;
        h1e  = 1.;
        mlt  = x;
        mlte = x+tol;
        k = 1;
        while 1
            u  = c(k) * mlt;
            ue = c(k) * mlte;
            h1  = h1  + u;
            h1e = h1e + ue;
            if k == m || (abs(u/h1) <= tol && abs(ue/h1e) <= tol)
                break
            end
            k = k + 1;
            mlt  = mlt  *  x;
            mlte = mlte * (x+tol);
        end

        % Newton iteration
        recip = 1/h1;
        P_new = P + (recip - P)/( (recip - 1/h1e)/tol + 1 );

        if abs(P - P_new) <= tol
            P = P_new;
            return
        end

        P = P_new;
    end

    P = -1;

end

