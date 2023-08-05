#!/usr/bin/env python3
# Closest values
# jill-jenn vie et christoph durr - 2014-2015


# snip{
def closest_values(L):
    """Closest values

    :param L: list of values
    :returns: two values from L with minimal distance
    :modifies: the order of L
    :complexity: O(n log n), for n=len(L)
    """
    assert len(L) >= 2
    L.sort()
    valmin, argmin = min((L[i] - L[i - 1], i) for i in range(1, len(L)))
    return L[argmin - 1], L[argmin]
# snip}


if __name__ == "__main__":
    L = [0, 2]
    assert(closest_values(L) == (0, 2))
    L = list(range(0, 1000000, 10)) + [56]
    assert(closest_values(L) == (56, 60))
