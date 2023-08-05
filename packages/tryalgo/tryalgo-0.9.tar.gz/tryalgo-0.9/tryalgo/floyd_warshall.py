#!/usr/bin/env python3
# All pairs shortest paths by Floyd-Warshall
# jill-jenn vie et christoph durr - 2014-2015

try:
    from graph import read_graph, write_graph
except ImportError:
    from . graph import read_graph, write_graph


# snip{
def floyd_warshall(weight):
    """All pairs shortest paths by Floyd-Warshall

    :param weight: edge weight matrix
    :modifies: weight matrix to contain distances in graph
    :returns: true if there are negative cycles
    :complexity: :math:`O(|V|^3)`
    """
    V = range(len(weight))
    for k in V:
        for u in V:
            for v in V:
                weight[u][v] = min(weight[u][v],
                                   weight[u][k] + weight[k][v])
    for v in V:
        if weight[v][v] < 0:      # cycle négatif détecté
            return True
    return False
# snip}


if __name__ == '__main__':
    # [!] O(n^3) sur des graphes à 500 sommets dure qq minutes
    for testfile in ['gdw_n500_big3', 'gdw_n500_big4',
                     'gdw_n5_graph',  'gdw_n5_isolated', 'gdw_n5_unreachable',
                     'gdwn_n25_grid', 'gdwn_n25_grid_disconnected_neg_cycle']:
        fullpath = "../../data/%s.txt" % testfile
        graph, weight = read_graph(fullpath, directed=False,
                                   weighted=True, default_weight=float('inf'))
        weight_before = [row[:] for row in weight]
        has_negative_cycle = floyd_warshall(weight)
        print(testfile, 'has_negative_cycle =', has_negative_cycle)
        write_graph("../../data/floyd_warshall_%s.dot" % testfile, graph,
                    directed=False, arc_label=weight_before,
                    node_label=weight[0])
