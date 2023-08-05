#!/usr/bin/env python3
# Solving Sudoku
# jill-jenn vie et christoph durr - 2014-2015

try:
    from dancing_links import dancing_links
except ImportError:
    from . dancing_links import dancing_links

__all__ = ["sudoku"]

# snip{
N = 3        # global constants
N2 = N * N
N4 = N2 * N2

# les ensembles
def assignation(r, c, v): return r * N4 + c * N2 + v

def row(a): return a // N4
def col(a): return (a // N2) % N2
def val(a): return a % N2
def blk(a): return (row(a) // N) * N + col(a) // N

# les éléments à couvrir
def rc(a): return row(a) * N2 + col(a)
def rv(a): return row(a) * N2 + val(a) + N4
def cv(a): return col(a) * N2 + val(a) + 2 * N4
def bv(a): return blk(a) * N2 + val(a) + 3 * N4


def sudoku(G):
    """Solving Sudoku

    :param G: integer matrix with 0 at empty cells
    :returns boolean: True if grid could be solved
    :modifies: G will contain the solution
    :complexity: huge, but linear for usual published 9x9 grids
    """
    global N, N2, N4
    if len(G) == 16:              # for a 16 x 16 sudoku grid
        N, N2, N4 = 4, 16, 256
    e = 4 * N4
    univers = e + 1
    S = [[rc(a), rv(a), cv(a), bv(a)] for a in range(N4 * N2)]
    A = [e]
    for r in range(N2):
        for c in range(N2):
            if G[r][c] != 0:
                a = assignation(r, c, G[r][c] - 1)
                A += S[a]
    sol = dancing_links(univers, S + [A])
    if sol:
        for a in sol:
            if a < len(S):
                G[row(a)][col(a)] = val(a) + 1
        return True
    else:
        return False
# snip}


if __name__ == "__main__":
    T = "*E***D57*0B**F**"\
        "*46C8****9*1**5*"\
        "**7*********2**3"\
        "*0**A******F1*C*"\
        "**4*3A*1********"\
        "*9*****582**40E*"\
        "E*2*F**DA*359***"\
        "8****9*2*E64C7*D"\
        "1*9*73****E*0***"\
        "******FB****8***"\
        "*3*2*6*****9*B*1"\
        "6**BC***5D****9*"\
        "***DB876**C3****"\
        "*****29***5*A**C"\
        "*5*3*C**9*F***4E"\
        "B**********E**62"
    A = "0123456789ABCDEF"

    def prettyPrint(G):
        B = A + "*"
        l = ""
        for r in range(N2):
            for c in range(N2):
                l += B[G[r][c]-1]
                if c % N == N-1:
                    l += "|"
            l += "\n"
            if r % N == N-1:
                l += "-" * (N2 + N) + "\n"
        print(l)

    G = [[] for _ in range(16)]
    for i in range(256):
        r = G[i // 16]
        v = A.find(T[i])
        r.append(v + 1)

    prettyPrint(G)
    print(sudoku(G))
    prettyPrint(G)
