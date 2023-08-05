#!/usr/bin/env python3
# Breadth-first-search, bfs and OurQueue
# christoph dürr - jill-jênn vie - 2015

# snip{
from collections import deque


def bfs(graph, start=0):
    """Shortest path in unweighted graph by BFS

       :param graph: adjacency list
       :param start: source vertex
       :returns: distance table, precedence table
       :complexity: `O(|V|+|E|)`
       """
    to_visit = deque()
    dist = [float('inf')] * len(graph)
    prec = [None] * len(graph)
    dist[start] = 0
    to_visit.appendleft(start)
    while to_visit:              # une file vide évalue à Faux
        node = to_visit.pop()
        for neighbor in graph[node]:
            if dist[neighbor] == float('inf'):
                dist[neighbor] = dist[node] + 1
                prec[neighbor] = node
                to_visit.appendleft(neighbor)
    return dist, prec
# snip}


if __name__ == "__main__":
    # graphe complet plus un sommet isolé
    n = 7
    G = [[j for j in range(n) if j != i] for i in range(n)]   # graphe complet
    G.append([])                                              # sommet isolé
    assert bfs(G, 0) == ([0, 1, 1, 1, 1, 1, 1, float('inf')],
                         [None, 0, 0, 0, 0, 0, 0, None])

    # arbre binaire complet
    A = [[], [2, 3]] + [[2 * i, 2 * i + 1, i // 2] for i in range(2, 8)] + \
        [[i // 2] for i in range(8, 16)]
    assert bfs(A, 1) == ([float('inf'), 0, 1, 1, 2, 2, 2, 2,
                          3, 3, 3, 3, 3, 3, 3, 3],
                         [None, None, 1, 1, 2, 2, 3, 3, 4,
                          4, 5, 5, 6, 6, 7, 7])
