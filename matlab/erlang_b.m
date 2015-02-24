function P = erlang_b(M,E)
	% Inefficient computation of Erlang-B
	P = ( E^M / factorial(M) ) / sum( E.^(0:M) ./ factorial(0:M) );
end

