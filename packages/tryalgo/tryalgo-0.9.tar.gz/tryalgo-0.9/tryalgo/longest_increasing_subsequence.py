#!/usr/bin/env python3
# Longest increasing subsequence
# jill-jenn vie et christoph durr - 2014-2015

# snip{
from bisect import bisect_left


def longest_increasing_subsequence(x):
    """Longest increasing subsequence

    :param x: sequence
    :returns: longest strictly increasing subsequence y
    :complexity: `O(|x|*log(|y|))`
    """
    n = len(x)
    p = [None] * n
    h = [None]
    b = [float('-inf')]  # - infinity
    for i in range(n):
        if x[i] > b[-1]:
            p[i] = h[-1]
            h.append(i)
            b.append(x[i])
        else:
            #   -- recherche dichotomique: b[k - 1] < x[i] <= b[k]
            k = bisect_left(b, x[i])
            h[k] = i
            b[k] = x[i]
            p[i] = h[k - 1]
    # extraire solution
    q = h[-1]
    s = []
    while q is not None:
        s.append(x[q])
        q = p[q]
    return s[::-1]
# snip}

if __name__ == "__main__":
    L = list(range(0, 10, 2))
    assert longest_increasing_subsequence(L) == L
    assert longest_increasing_subsequence(L * 2) == L
    assert longest_increasing_subsequence(L[::-1]) == [0]
    assert longest_increasing_subsequence([]) == []
    assert longest_increasing_subsequence([7]) == [7]
    assert longest_increasing_subsequence([-2, 4, 4]) == [-2, 4]
    assert longest_increasing_subsequence([4, 4, -2]) == [-2]
    Q = [3, 1, 4, 1, 5, 9, 2, 6, 5, 4, 5, 3, 9, 7, 9]
    A = [1, 2, 4, 5, 7, 9]
    assert longest_increasing_subsequence(Q) == A
