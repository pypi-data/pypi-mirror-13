#!/usr/bin/env python3
# Largest area rectangle in a binary matrix
# plus grand rectangle monochromatique
# jill-jenn vie et christoph durr - 2014-2015

try:
    from rectangles_from_histogram import rectangles_from_histogram
except ImportError:
    from . rectangles_from_histogram import rectangles_from_histogram


# snip{
def rectangles_from_grid(P, noir=1):
    """Largest area rectangle in a binary matrix

    :param P: matrix
    :param noir: search for rectangles filled with value noir
    :returns: area, left, top, right, bottom of optimal rectangle
             consisting of all (i,j) with
             left <= j < right and top <= i <= bottom
    :complexity: linear
    """
    rows = len(P)
    cols = len(P[0])
    t = [0] * cols
    best = None
    for i in range(rows):
        for j in range(cols):
            if P[i][j] == noir:
                t[j] += 1
            else:
                t[j] = 0
        (area, left, height, right) = rectangles_from_histogram(t)
        alt = (area, left, i, right, i-height)
        if best is None or alt > best:
            best = alt
    return best
# snip}


if __name__ == "__main__":
    R = ["10110111",
         "01000101",
         "11011000",
         "00111010",
         "11011101",
         "01000101"]
    assert rectangles_from_grid(R, noir='1') == (6, 3, 4, 5, 1)
