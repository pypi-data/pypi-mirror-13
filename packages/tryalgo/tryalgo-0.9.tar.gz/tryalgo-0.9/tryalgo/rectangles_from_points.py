#!/usr/bin/env python3
# How many rectangles can be formed from a set of points
# jill-jenn vie et christoph durr - 2014-2015


# snip{
def rectangles_from_points(S):
    """How many rectangles can be formed from a set of points

    :param S: list of points, as coordinate pairs
    :returns: the number of rectangles
    :complexity: :math:`O(n^2)`
    """
    answ = 0
    pairs = {}
    for j in range(len(S)):
        for i in range(j):
            px, py = S[i]
            qx, qy = S[j]
            center = (px + qx, py + qy)
            dist = (px - qx) * (px - qx) + (py - qy) * (py - qy)
            sign = (center, dist)
            if sign in pairs:
                answ += len(pairs[sign])
                pairs[sign].append((i, j))
            else:
                pairs[sign] = [(i, j)]
    return answ
# snip}

if __name__ == "__main__":
    L = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 2), (3, 1), (2, 0), (1, 0)]
    A = [0, 0, 0, 0, 0, 1, 3, 6]
    while L:
        assert rectangles_from_points(L) == A[-1]
        A.pop()
        L.pop()
