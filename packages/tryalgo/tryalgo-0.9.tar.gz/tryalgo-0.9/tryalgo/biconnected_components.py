#!/usr/bin/env python3
# bi-connected components, cut vertices and cut cut-nodes
# jill-jenn vie et christoph durr - 2015

try:
    from graph import write_graph
except ImportError:
    from . graph import write_graph


# snip{
# pour faciliter la lecture les variables sont sans préfixe dfs_
def cut_nodes_edges(graph):
    """Bi-connected components

    :param graph: adjacency list
    :returns: a tuple with the list of cut-nodes and the list of cut-edges
    :complexity: `O(|V|+|E|)`
    """
    n = len(graph)
    time = 0
    num = [None] * n
    low = [n] * n
    father = [None] * n        # father[v] = père de v, None si racine
    critical_childs = [0] * n  # c_childs[u] = nb fils v tq low[v] >= num[u]
    times_seen = [-1] * n
    for start in range(n):
        if times_seen[start] == -1:               # initier parcours DFS
            times_seen[start] = 0
            to_visit = [start]
            while to_visit:
                node = to_visit[-1]
                if times_seen[node] == 0:         # début traitement
                    num[node] = time
                    time += 1
                    low[node] = float('inf')
                children = graph[node]
                if times_seen[node] == len(children):  # fin traitement
                    to_visit.pop()
                    up = father[node]             # propager low au père
                    if up is not None:
                        low[up] = min(low[up], low[node])
                        if low[node] >= num[up]:
                            critical_childs[up] += 1
                else:
                    child = children[times_seen[node]]   # prochain arc
                    times_seen[node] += 1
                    if times_seen[child] == -1:   # pas encore visité
                        father[child] = node      # arc de liaison
                        times_seen[child] = 0
                        to_visit.append(child)    # (dessous) arc retour
                    elif num[child] < num[node] and father[node] != child:
                        low[node] = min(low[node], num[child])
    cut_edges = []
    cut_nodes = []                                # extraire solution
    for node in range(n):
        if father[node] == None:                  # caractérisations
            if critical_childs[node] >= 2:
                cut_nodes.append(node)
        else:                                     # nœuds internes
            if critical_childs[node] >= 1:
                cut_nodes.append(node)
            if low[node] >= num[node]:
                cut_edges.append((father[node], node))
    return cut_nodes, cut_edges
# snip}

if __name__ == "__main__":
    G0 = {
        0: [1, 2, 5],
        1: [0, 5],
        2: [0, 3, 4],
        3: [2, 4, 5, 6],
        4: [2, 3, 5, 6],
        5: [0, 1, 3, 4],
        6: [3, 4],
    }
    G1 = [[], [2, 4], [1, 3, 5], [2, 4, 5], [3, 1], [2, 3, 6, 7], [5, 7, 8],
          [5, 6, 8], [6, 7, 9], [8, 10, 11], [9, 11], [9, 10]]
    G2 = {
        0: [2, 5],
        1: [3, 8],
        2: [0, 3, 5],
        3: [1, 2, 6, 8],
        4: [7],
        5: [0, 2],
        6: [3, 8],
        7: [4],
        8: [1, 3, 6],
    }
    assert cut_nodes_edges(G0) == ([], [])
    assert cut_nodes_edges(G1) == ([5, 8, 9], [(8, 9)])
    assert cut_nodes_edges(G2) == ([2, 3], [(2, 3), (4, 7)])
    assert cut_nodes_edges([[]]) == ([], [])
    assert cut_nodes_edges([[1], [0]]) == ([], [(0, 1)])
    assert cut_nodes_edges([[1], [0, 2], [1]]) == ([1], [(0, 1), (1, 2)])
    assert cut_nodes_edges([[1, 2], [0, 2], [0, 1, 3], [2]]) == ([2], [(2, 3)])
    for G, name in [(G1, 'g1'), (G2, 'g2')]:
        cut_nodes, cut_edges = cut_nodes_edges(G)
        write_graph("../../data/biconnexes_%s.dot" % name, G,
                    node_mark=cut_nodes, arc_mark=cut_edges)
