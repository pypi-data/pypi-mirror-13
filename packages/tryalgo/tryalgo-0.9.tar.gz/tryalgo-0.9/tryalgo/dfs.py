#!/usr/bin/env python3
# Depth first search - DFS
# jill-jenn vie et christoph durr - 2015


# snip{ dfs-recursive
def dfs_recursive(graph, node, seen):
    """DFS, recursive implementation

    :param graph: adjacency list
    :param node: to start graph exploration
    :param seen: boolean table, will be set true for the connected component
          containing node.
    :complexity: `O(|V|+|E|)`
    """
    seen[node] = True
    for neighbor in graph[node]:
        if not seen[neighbor]:
            dfs_recursive(graph, neighbor, seen)
# snip}


# snip{ dfs-iterative
def dfs_iterative(graph, start, seen):
    """DFS, iterative implementation

    :param graph: adjacency list
    :param node: to start graph exploration
    :param seen: boolean table, will be set true for the connected component
          containing node.
    :complexity: `O(|V|+|E|)`
    """
    seen[start] = True
    to_visit = [start]
    while to_visit:
        node = to_visit.pop()
        for neighbor in graph[node]:
            if not seen[neighbor]:
                seen[neighbor] = True
                to_visit.append(neighbor)
# snip}


def dfs_grid_recursive(grid, i, j, mark='X', free='.'):
    height = len(grid)
    width = len(grid[0])
    grid[i][j] = mark              # marquer passage
    for ni, nj in [(i + 1, j), (i, j + 1),
                   (i - 1, j), (i, j - 1)]:
        if 0 <= ni < height and 0 <= nj < width:
            if grid[ni][nj] == free:
                dfs_grid(grid, ni, nj)


# snip{ dfs-grid
def dfs_grid(grid, i, j, mark='X', free='.'):
    """explore grid starting from cell (i,j)

    :param grid: matrix, 4-neighborhood
    :param i,j: cell in this matrix
    :param free: symbol for walkable cells
    :param mark: symbol to overwrite visited vertices
    :complexity: linear
    """
    height = len(grid)
    width = len(grid[0])
    to_visit = [(i, j)]
    grid[i][j] = mark
    while to_visit:
        i1, j1 = to_visit.pop()
        for i2, j2 in [(i1 + 1, j1), (i1, j1 + 1),
                       (i1 - 1, j1), (i1, j1 - 1)]:
            if 0 <= i2 < height and 0 <= j2 < width and grid[i2][j2] == free:
                grid[i2][j2] = mark  # marquer visite
                to_visit.append((i2, j2))
# snip}


def find_cycle(graph):
  """find a cycle in an undirected graph

  :param graph: adjacency list, undirected graph
  :returns: list of vertices in a cycle or None
  :complexity: `O(|V|+|E|)`
  """
  n = len(graph)
  prec  = [None] * n              # ancestor marks for visited vertices
  for u in range(n):
    if prec[u] is None:           # unvisited vertex
      S = [u]                     # start new DFS
      prec[u] = u                 # mark root (not necessary for this algorithm)
      while S:
        u = S.pop()
        for v in graph[u]:        # for all neighbors
          if v != prec[u]:        # except arcs to father in DFS tree
            if prec[v] is not None:
              cycle = [v, u]      # cycle found, (u,v) is a back edge
              while u != prec[v] and u != prec[u]:  # for directed graphs
                u = prec[u]       # climb up the tree
                cycle.append(u)
              return cycle
            else:
              prec[v] = u         # v is new vertex in tree
              S.append(v)
  return None


if __name__ == "__main__":
    def reachable(graph, start, dfs):
        """Nodes reachable from a start vertex

        :param graph: adjacency list
        :param start: start vertex
        :param dfs: implementation of DFS to use
        :returns: list of vertices in the component containing start
        """
        n = len(graph)
        seen = [False] * n
        dfs(graph, start, seen)
        return [node for node in range(n) if seen[node]]

    n = 100000
    G = [[v for v in range(u + 1, min(u + 10, n))] for u in range(n)]
    assert reachable(G, 3, dfs_iterative) == list(range(3, n))

    # tests sur la profondeur possible de la récursion
    # from random import *
    # from sys    import *

    # G2 = [[] for u in range(n)]
    # for _ in range(15 * n):
    #     u = randint(0, n - 1)
    #     v = randint(0, n - 1)
    #     G2[u].append(v)
    #     G2[v].append(u)

    # setrecursionlimit(2 * n + 10)
    # graph = G2
    # seen = [None] * n
    # dfs(0)
    # print( "aha")
    # exit(0)

    for f in [dfs_recursive, dfs_iterative]:
        assert reachable([[]], 0, f) == [0]
        assert reachable([[1], []], 0, f) == [0, 1]
        assert reachable([[1], []], 1, f) == [1]
        assert reachable([[1], [2], []], 1, f) == [1, 2]
        assert reachable([[1, 5], [2, 3, 5], [3],
                          [4, 5], [5], []], 2, f) == [2, 3, 4, 5]

    inTextGrid = """\
##########
.....#...#
####.###.#
#..#.#...#
#..#.#.###
###..#.#.#
#.#.####.#
#........#
########.#\
"""

    outTextGrid = """\
##########
XXXXX#...#
####X###.#
#..#X#...#
#..#X#.###
###XX#.#X#
#X#X####X#
#XXXXXXXX#
########X#\
"""
    grid = [list(line.strip()) for line in inTextGrid.split('\n')]
    out = [list(line.strip()) for line in outTextGrid.split('\n')]
    dfs_grid(grid, 1, 0)
    assert str(grid) == str(out)

    assert find_cycle([]) is None
    assert find_cycle([[]]) is None
    assert find_cycle([[], []]) is None
    assert find_cycle([[1], [0]]) is None
    assert find_cycle([[], [2], [1]]) is None
    assert set(find_cycle([[1, 2], [0, 2], [0, 1]])) == {1,2,0}
    # directed graph could generate infinite loop
    print( find_cycle([[1, 2], [0], [0], [2, 4], [3]]) )
    print( find_cycle([[1, 2], [0], [0]]) )
    print( find_cycle([[1, 2], [0], [0], [4, 5], [3, 5], [3, 4]]) )
