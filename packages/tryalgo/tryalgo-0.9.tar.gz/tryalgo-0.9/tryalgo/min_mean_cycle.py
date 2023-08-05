#!/usr/bin/env python3
# Minimum mean cycle by Karp
# jill-jenn vie et christoph durr - 2014-2015


# snip{
def min_mean_cycle(graph, weight, start=0):
    """Minimum mean cycle by Karp

    :param graph: adjacency list, directed graph
    :param weight: matrix
    :param int start: vertex that should be contained in cycle
    :returns: cycle as vertex list, average arc weights
             or None if there is no cycle from start
    :complexity:  `O(|V|*|E|)`
    """
    INF = float('inf')
    n = len(graph)                  # calculer distances
    dist = [[INF] * n]
    prec = [[None] * n]
    dist[0][start] = 0
    for ell in range(1, n + 1):
        dist.append([INF] * n)
        prec.append([None] * n)
        for node in range(n):
            for neighbor in graph[node]:
                alt = dist[ell - 1][node] + weight[node][neighbor]
                if alt < dist[ell][neighbor]:
                    dist[ell][neighbor] = alt
                    prec[ell][neighbor] = node
    #                               -- détecter valeur optimale
    valmin = INF
    argmin = None
    for node in range(n):
        valmax = -INF
        argmax = None
        for k in range(n):
            alt = (dist[n][node] - dist[k][node]) / float(n - k)
            # ne pas diviser par float(n-k) pour le cycle de poids total min
            if alt >= valmax:     # par >= on cherche cycles simples
                valmax = alt
                argmax = k
        if argmax is not None and valmax < valmin:
            valmin = valmax
            argmin = (node, argmax)
    #                               -- extraire cycle
    if valmin == INF:             # -- il n'y a pas de cycle du tout
        return None
    C = []
    node, k = argmin
    for l in range(n, k, -1):
        C.append(node)
        node = prec[l][node]
    return C[::-1], valmin
# snip}

if __name__ == "__main__":
    W0 = [[None, -5,   None, None],
          [None, None, -3,      0],
          [9,    None, None,    2],
          [7,    0,    -1,   None]]
    W1 = [[None, 10, None], [None, -2, None], [None, None, -20]]
    W2 = [[None, 10, 10], [None, -8, -8], [None, -8, -8]]
    W3 = [[None, None], [0, -4]]

    A0 = ([2, 3, 1], -1./3)
    A1 = ([1], -2)
    A2 = ([1], -8)
    A3 = None

    def make_graph(weight):
        graph = [[] for _ in range(len(weight))]
        for u in range(len(graph)):
            for v in range(len(graph)):
                if weight[u][v] != None:
                    graph[u].append(v)
        return graph

    for weight, answ in [(W0, A0), (W1, A1), (W2, A2), (W3, A3)]:
        assert min_mean_cycle(make_graph(weight), weight) == answ
