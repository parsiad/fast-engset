function [P,n,status] = engset_newton(M,S,E,P,tol,n_max)
    % Default arguments
    if nargin < 4; P     =     0.5; end
    if nargin < 5; tol   = 2^(-24); end
    if nargin < 6; n_max =    2^10; end

    % Newton iteration
    status = 1;
    c = S-M;
    for n = 1:n_max+1
        h1 = hypergeom([1, -M],S-M+0,1-P-S/E);
        h2 = hypergeom([2,1-M],S-M+1,1-P-S/E);

        % Canot guarantee P_new >= 0
        %P_new = P + P * c * (1 - P * h1)/(M * P * P * h2 + c);

        % Guarantees P_new >= 0
        P_new = P + ( 1/h1 - P )/(M/c * h2/(h1*h1) + 1);

        if abs(P - P_new) <= tol
            % Iteration converged
            P = P_new;
            status = 0;
            break;
        end
        P = P_new;
    end
end

