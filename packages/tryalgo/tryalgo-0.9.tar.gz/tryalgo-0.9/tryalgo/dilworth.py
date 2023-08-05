#!/usr/bin/env python3
# Decompose DAG into a minimum number of chains
# jill-jenn vie et christoph durr - 2015

try:
    from graph import read_graph, write_graph
    from bipartite_matching import max_bipartite_matching
except ImportError:
    from . graph import read_graph, write_graph
    from . bipartite_matching import max_bipartite_matching


# snip{
def dilworth(graph):
    """Decompose a DAG into a minimum number of chains by Dilworth

    :param graph: adjacency list of a directed graph
    :assumes: graph is acyclic
    :returns: table giving for each vertex the number of its chains
    :complexity: same as matching
    """
    n = len(graph)
    match = max_bipartite_matching(graph)  # couplage maximum
    part = [None] * n                      # partition en chaînes
    nb_chains = 0
    for v in range(n - 1, -1, -1):         # dans l'ordre topologique inverse
        if part[v] is None:                # début d'une chaîne
            u = v
            while u is not None:           # suivre la chaîne
                part[u] = nb_chains        # marquer
                u = match[u]
            nb_chains += 1
    return part
# snip}


if __name__ == '__main__':
    G = [[1],
         [2, 3, 5],
         [6, 7],
         [7, 8],
         [5, 6],
         [8],
         [8],
         [],
         []]
    p = dilworth(G)
    write_graph(dotfile="../../data/dilworth.dot", graph=G,
                directed=True, node_label=p)
