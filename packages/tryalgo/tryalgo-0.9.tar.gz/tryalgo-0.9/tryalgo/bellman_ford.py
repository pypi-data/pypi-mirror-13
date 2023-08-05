#!/usr/bin/env python3
# Single source shortest paths by Bellman-Ford
# jill-jenn vie et christoph durr - 2014-2015

try:
    from graph import read_graph, write_graph
except ImportError:
    from . graph import read_graph, write_graph


# snip{
def bellman_ford(graph, weight, source=0):
    """ Single source shortest paths by Bellman-Ford

    :param graph: adjacency list
    :param weight: matrix, might be negative
    :returns: distance table
    :complexity: `O(|V|*|E|)`
    """
    n = len(graph)
    dist = [float('inf')] * n
    prec = [None] * n
    dist[source] = 0
    for nb_iterations in range(n):
        changed = False
        for node in range(n):
            for neighbor in graph[node]:
                alt = dist[node] + weight[node][neighbor]
                if alt < dist[neighbor]:
                    dist[neighbor] = alt
                    prec[neighbor] = node
                    changed = True
        if not changed:                   # point fixe
            return dist, prec, False
    return dist, prec, True
# snip}


if __name__ == '__main__':
    for testfile in ['gdw_n11348_paris', 'gdw_n500_big3', 'gdw_n500_big4',
                     'gdw_n5_graph',  'gdw_n5_isolated', 'gdw_n5_unreachable',
                     'gdwn_n25_grid', 'gdwn_n25_grid_disconnected_neg_cycle']:
        fullpath = "../../data/%s.txt" % testfile
        graph, weight = read_graph(fullpath, directed=False, weighted=True)
        dist, prec, has_neg_cycle = bellman_ford(graph, weight, len(graph) - 1)
        print(testfile, 'has_negative_cycle =', has_neg_cycle)
        write_graph("../../data/bellman_ford_%s.dot" % testfile,
                    graph, directed=False, arc_label=weight, node_label=dist)
