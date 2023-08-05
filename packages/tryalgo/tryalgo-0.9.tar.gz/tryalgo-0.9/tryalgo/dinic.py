#!/usr/bin/env python3
# Maximum flow by Dinic
# jill-jênn vie et christoph dürr - 2015


from collections import deque
from sys import setrecursionlimit
try:
    from graph import read_graph, write_graph, \
                      add_reverse_arcs, make_flow_labels
except ImportError:
    from . graph import read_graph, write_graph, \
                        add_reverse_arcs, make_flow_labels


setrecursionlimit(5010)  # nécessaire pour de grands graphes


# snip{
def dinic(graph, capacity, source, target):
    """Maximum flow by Dinic

    :param graph: adjacency list
    :param capacity: matrix
    :param int source: vertex
    :param int target: vertex
    :returns: skew symmetric flow matrix, flow value
    :complexity: :math:`O(|V|^2 |E|)`
    """
    assert source != target
    add_reverse_arcs(graph, capacity)
    Q = deque()
    total = 0
    n = len(graph)
    flow = [[0] * n for u in range(n)]   # flot init. vide
    while True:                   # répéter tant qu'on peut augmenter
        Q.appendleft(source)
        lev = [None] * n          # construire niveaux, None = inaccessible
        lev[source] = 0           # par parcours BFS
        while Q:
            u = Q.pop()
            for v in graph[u]:
                if lev[v] is None and capacity[u][v] > flow[u][v]:
                    lev[v] = lev[u] + 1
                    Q.appendleft(v)

        if lev[target] is None:   # arrêt si puits inaccessible
            return flow, total
        # UB = borne supérieure
        UB = sum(capacity[source][v] for v in graph[source]) - total
        total += _dinic_step(graph, capacity, lev, flow, source, target, UB)


def _dinic_step(graph, capacity, lev, flow, u, target, limit):
    """ tenter de pousser le plus de flot de u à target, sans dépasser limit
    """
    if limit <= 0:
        return 0
    if u == target:
        return limit
    val = 0
    for v in graph[u]:
        residuel = capacity[u][v] - flow[u][v]
        if lev[v] == lev[u] + 1 and residuel > 0:
            z = min(limit, residuel)
            aug = _dinic_step(graph, capacity, lev, flow, v, target, z)
            flow[u][v] += aug
            flow[v][u] -= aug
            val += aug
            limit -= aug
    if val == 0:
        lev[u] = None         # sommet non franchissable à enlever
    return val
# snip}


if __name__ == "__main__":
    for testfile in ['guw_flow4a', 'guw_flow4b', 'guw_flow6', 'gdw_flow12']:
        fullpath = "../../data/%s.txt" % testfile
        directed = (testfile[1] == 'd')
        graph, capac = read_graph(fullpath, directed=directed,
                                  weighted=True, default_weight=0)
        flow, val = dinic(graph, capac, 0, len(graph) - 1)
        write_graph("../../data/dinic_%s.dot" % testfile, graph,
                    directed=True, comment="flow value = %g" % val,
                    arc_label=make_flow_labels(graph, flow, capac))
