#!/usr/bin/env python3
# Largest Rectangular Area in a Histogram
# jill-jenn vie et christoph durr - 2014-2015

from random import randint


# snip{
def rectangles_from_histogram(H):
    """Largest Rectangular Area in a Histogram

    :param H: histogram table
    :returns: area, left, height, right, rect. is [0, height] * [left, right)
    :complexity: linear
    """
    best = (float('-inf'), 0, 0, 0)
    S = []
    H2 = H + [float('-inf')]  # élément supplémentaire pour vider la pile
    for right in range(len(H2)):
        x = H2[right]
        left = right
        while len(S) > 0 and S[-1][1] >= x:
            left, height = S.pop()
            #                (surface, gauche, hauteur, droite)
            rect = (height * (right - left), left, height, right)
            if rect > best:
                best = rect
        S.append((left, x))
    return best
# snip}


if __name__ == "__main__":
    for L in range(100):
        T = [randint(1, 100) for _ in range(L)]
        best = (float('-inf'), 0, 0)
        for j in range(1, L + 1):
            for i in range(j):
                area = ((j - i) * min(T[i:j]), i, j)
                if area > best:
                    best = area
        assert best[0] == rectangles_from_histogram(T)[0]
