#!/usr/bin/env python3
# Maximum flow by Ford-Fulkerson
# jill-jenn vie et christoph durr - 2014-2015

from sys import setrecursionlimit
try:
    from graph import read_graph, write_graph, \
                      add_reverse_arcs, make_flow_labels
except ImportError:
    from . graph import read_graph, write_graph, \
                        add_reverse_arcs, make_flow_labels


# snip{
def _augment(graph, capacity, flow, val, u, target, visit):
    """Find an augmenting path from u to target with value at most val"""
    visit[u] = True
    if u == target:
        return val
    for v in graph[u]:
        cuv = capacity[u][v]
        if not visit[v] and cuv > flow[u][v]:  # arc franchissable
            res = min(val, cuv - flow[u][v])
            delta = _augment(graph, capacity, flow, res, v, target, visit)
            if delta > 0:
                flow[u][v] += delta            # augmenter le flot
                flow[v][u] -= delta
                return delta
    return 0


def ford_fulkerson(graph, capacity, s, t):
    """Maximum flow by Ford-Fulkerson

    :param graph: adjacency list
    :param capacity: matrix
    :param int s: source vertex
    :param int t: target vertex

    :returns: flow matrix, flow value
    :complexity: `O(|V|*|E|*max_capacity)`
    """
    add_reverse_arcs(graph, capacity)
    n = len(graph)
    flow = [[0] * n for _ in range(n)]
    INF = float('inf')
    while _augment(graph, capacity, flow, INF, s, t, [False] * n) > 0:
            pass                               # corps de boucle vide
    return (flow, sum(flow[s]))                # flot, valeur du flot
# snip}


if __name__ == "__main__":
    for testfile in ['guw_flow4a', 'guw_flow4b', 'guw_flow6', 'gdw_flow12']:
        fullpath = "../../data/%s.txt" % testfile
        directed = (testfile[1] == 'd')
        graph, capac = read_graph(fullpath, directed=directed,
                                  weighted=True, default_weight=0)
        flow, val = ford_fulkerson(graph, capac, 0, len(graph)-1)
        write_graph("../../data/ford-fulkerson_%s.dot" % testfile, graph,
                    directed=True, comment="flow value = %g" % val,
                    arc_label=make_flow_labels(graph, flow, capac))
