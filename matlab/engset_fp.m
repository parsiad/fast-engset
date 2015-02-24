function [P,n,status,P_list] = engset_fp(M,S,E,P,tol,n_max)
    % Default arguments
    if nargin < 4; P     =     0.5; end
    if nargin < 5; tol   = 2^(-24); end
    if nargin < 6; n_max =    2^10; end

    P_list = [];

    % Lipschitz constant
    c = S-M;
    h1 = hypergeom([1, -M],c  ,1-S/E);
    h2 = hypergeom([2,1-M],c+1,1-S/E);
    q = M/c * h2 / (h1 * h1);

    % Number of iterations to get |P - P_n| < tol
    %P_new = 1/hypergeom([1,-M],c,1-P-S/E);
    %if q < 1.
        % Lipschitz constant < 1; use good bound on n_max
        %n_cap = ceil( log( tol / abs(P_new - P) * (1-q) ) / log(q) );
        %n_max = min(n_cap, n_max);
    %end

    % Fixed point iteration
    %P = P_new;
    status = 1;
    for n = 1:n_max+1
        P_new = 1/hypergeom([1,-M],c,1-P-S/E);
        P_list = [P_list P_new];
        if abs(P - P_new) <= tol
            % Iteration converged
            P = P_new;
            status = 0;
            break;
        end
        P = P_new;
    end
end

