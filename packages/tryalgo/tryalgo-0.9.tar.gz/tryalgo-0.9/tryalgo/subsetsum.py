#!/usr/bin/env python3
# subsetsum
# jill-jenn vie et christoph durr - 2015


# snip{ subsetsum
def subset_sum(x, R):
    """Subsetsum

    :param x: table of non negative values
    :param R: target value
    :returns boolean: True if a subset of x sums to R
    :complexity: O(n*R)
    """
    b = [False] * (R + 1)
    b[0] = True
    for xi in x:
        for s in range(R, xi - 1, -1):
            b[s] |= b[s - xi]
    return b[R]
# snip}


# snip{ coinchange
def coin_change(x, R):
    """Coin change

    :param x: table of non negative values
    :param R: target value
    :returns boolean: True if there is a non negative linear combination
             of x that has value R
    :complexity: O(n*R)
    """
    b = [False] * (R + 1)
    b[0] = True
    for xi in x:
        for s in range(xi, R + 1):
            b[s] |= b[s - xi]
    return b[R]
# snip}


if __name__ == "__main__":
    L = [518533,
         1037066,
         2074132,
         1648264,
         796528,
         1593056,
         686112,
         1372224,
         244448,
         488896,
         977792,
         1955584,
         1411168,
         322336,
         644672,
         1289344,
         78688,
         157376,
         314752,
         629504,
         1259008]
    assert subset_sum(L, 2463098) == True
    assert subset_sum(L, 2463099) == False
    C = [3, 5, 11]
    B = [b for b in range(30) if not coin_change(C, b)]
    assert B == [1, 2, 4, 7]
