#!/usr/bin/env python3
# subsetsum
# jill-jenn vie et christoph durr - 2015


# snip{
def three_partition(x):
    """partition a set of integers in 3 parts of same total value

    :param x: table of non negative values
    :returns triplet: of the integers encoding the sets, or None otherwise
    :complexity: :math:`O(2^{2n})`
    """
    f = [0] * (1 << len(x))
    for i in range(len(x)):
        for S in range(1 << i):
            f[S | (1 << i)] = f[S] + x[i]
    for A in range(1 << len(x)):
        for B in range(1 << len(x)):
            if A & B == 0 and f[A] == f[B] and 3 * f[A] == f[-1]:
                return (A, B, ((1 << len(x)) -1) ^ A ^ B)
    return None
# snip}


if __name__ == "__main__":
    assert subset_3parts([5, 5, 3, 2]) == (1, 2, 12)
    assert subset_3parts([1, 4, 5, 3, 2]) == (3, 4, 24)
    assert subset_3parts([10, 2, 3]) == None
