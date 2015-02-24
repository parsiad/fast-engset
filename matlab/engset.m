function P = engset(M,S,E)
	% Just use Newton's method

	P = zeros(size(S));

	for i = 1:size(S, 1)
		for j = 1:size(S, 2)
			[p,~,~] = engset_newton(M, S(i,j) ,E);
			P(i, j) = p;
		end
	end
end
