function [P,n,status] = engset_bisect(M,S,E,tol,n_max)
    % Default arguments
    if nargin < 4; tol   = 2^(-24); end
    if nargin < 5; n_max =    2^10; end

    % Number of iterations that to get |P - P_n| < tol
    %n_cap = ceil( log2( 1 / tol ) );
    %n_max = min(n_cap, n_max);

    % Bisection
    lo = 0;
    hi = 1;
    for n = 1:n_max+1
        P = (lo + hi) / 2;
        if (hi - lo)/2 <= tol
            status = 0;
            break;
        end
        if 1/hypergeom([1,-M],S-M,1-P-S/E)-P < 0
            hi = P;
        else
            lo = P;
        end
    end
end

