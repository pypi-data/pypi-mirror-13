#!/usr/bin/env python3
# Orienting mirrors to allow connectivity by a laser beam
# jill-jenn vie et christoph durr - 2014-2015

# snip{ laser-miroir-preparation
# directions
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3
# orientations None:? 0:/ 1:\

# arrivée UP            LEFT        DOWN          RIGHT
reflex = [[RIGHT, LEFT], [DOWN, UP],  [LEFT, RIGHT], [UP, DOWN]]


def laser_mirrors(rows, cols, mir):
    """Orienting mirrors to allow reachability by laser beam

    :param int rows:
    :param int cols: rows and cols are the dimension of the grid
    :param mir: list of mirror coordinates, except
                mir[0]= laser entrance,
                mir[-1]= laser exit.
    :complexity: :math:`O(2^n)`
    """
    # construire les structures
    n = len(mir)
    orien = [None] * (n + 2)
    orien[n] = 0  # orientations arbitraires pour les ouvertures
    orien[n + 1] = 0
    _next = [[None for _dir in range(4)] for i in range(n + 2)]
    L = [(mir[i][0], mir[i][1], i) for i in range(n)]
    L.append((0, -1, n))                  # entrée
    L.append((0, cols, n + 1))              # sortie
    last_r = None
    for (r, c, i) in sorted(L):           # balayage par ligne
        if last_r == r:
            _next[i][LEFT] = last_i
            _next[last_i][RIGHT] = i
        last_r, last_i = r, i
    last_c = None
    for (r, c, i) in sorted(L, key=lambda tup_rci: (tup_rci[1], tup_rci[0])):
        if last_c == c:                   # balayage par colonne
            _next[i][UP] = last_i
            _next[last_i][DOWN] = i
        last_c, last_i = c, i
    if solve(_next, orien, n, RIGHT):      # exploration
        return orien[:n]
    else:
        return None
# snip}


# snip{ laser-miroir-exploration
def solve(next, orien, i, _dir):
    """Can a laser leaving mirror i in direction _dir reach exit ?

    :param i: mirror index
    :param _dir: direction leaving mirror i
    :param orient: orient[i]=orientation of mirror i
    :param _next: _next[i][_dir]=next mirror reached
                 when leaving i in direction _dir
    """
    assert orien[i] != None
    j = _next[i][_dir]
    if j is None:          # cas de base
        return False
    if j == len(orien) - 1:
        return True
    if orien[j] is None:   # tester les 2 orientations
        for x in [0, 1]:
            orien[j] = x
            if solve(_next, orien, j, reflex[_dir][x]):
                return True
        orien[j] = None
        return False
    else:
        return solve(_next, orien, j, reflex[_dir][orien[j]])
# snip}

if __name__ == "__main__":
    assert laser_mirrors(2, 2, [(0, 0), (0, 1),
                                (1, 0), (1, 1)]) == [1, 0, 1, 0]
    assert laser_mirrors(7, 8, [(0, 1), (0, 4), (0, 6), (2, 3), (2, 4),
                                (4, 1), (4, 4), (4, 6), (6, 0), (6, 3),
                                (6, 4)]) == [1, None, 0, 0, 1, 1,
                                             0, 0, None, 1, 0]
    assert laser_mirrors(5, 4, [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3),
                                (2, 0), (2, 1), (2, 2), (2, 3), (3, 0),
                                (3, 1), (3, 2), (3, 3), (4, 0), (4, 1),
                                (4, 2), (4, 3)]) == None
