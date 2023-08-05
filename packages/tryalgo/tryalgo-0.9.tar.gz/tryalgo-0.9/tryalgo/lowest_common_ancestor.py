#!/usr/bin/env python3
# Lowest common ancestor
# jill-jenn vie et christoph durr - 2014-2015
# http://leetcode.com/2011/11/longest-palindromic-substring-part-ii.html

try:
    from range_minimum_query import Range_min_query
except ImportError:
    from . range_minimum_query import Range_min_query


def log2floor(n):
    """ log of n in base 2 rounded down """
    k = -1
    assert n >= 0
    while n:
        k += 1
        n >>= 1
    return k


def log2ceil(n):
    """ log of n in base 2 rounded up """
    return log2floor(n - 1) + 1


# snip{ lowest_common_ancestor_by_shortcuts
class LowestCommonAncestor_by_shortcuts:
    """Lowest common ancestor data structure using shortcuts to ancestors
    """
    def __init__(self, prec):
        """builds the structure from a given tree

        :param nodes: all indices in prec, root = 0
        :param prec: father for every node, with prec[0] = 0
        :assumes: prec[node] < node
        :complexity: O(n log n), with n = len(nodes)
        """
        n = len(prec)
        self.level = [None] * n        # construit les niveaux
        self.level[0] = 0
        for u in range(1, n):
                self.level[u] = 1 + self.level[prec[u]]
        depth = log2ceil(max(self.level[u] for u in nodes)) + 1
        self.anc = [[0] * n for _ in range(depth)]
        for u in range(n):
            self.anc[0][u] = prec[u]
        for k in range(1, depth):
            for u in range(n):
                self.anc[k][u] = self.anc[k - 1][self.anc[k - 1][u]]

    def query(self, u, v):
        """:returns: the lowest common ancestor of u and v
        :complexity: O(log n)
        """
        # -- supposer que v n'est pas plus haut que u dans l'arbre
        if self.level[u] > self.level[v]:
            u, v = v, u
        # -- ramener v au même niveau que u
        depth = len(self.anc)
        for k in range(depth-1, -1, -1):
            if self.level[u] <= self.level[v] - (1 << k):
                v = self.anc[k][v]
        assert self.level[u] == self.level[v]
        if u == v:
            return u
        # -- remonter jusqu'à l'ancêtre commun le plus proche
        for k in range(depth-1, -1, -1):
            if self.anc[k][u] != self.anc[k][v]:
                u = self.anc[k][u]
                v = self.anc[k][v]
        assert self.anc[0][u] == self.anc[0][v]
        return self.anc[0][u]
# snip}


# snip{ lowest_common_ancestor_by_rmq
class LowestCommonAncestor_by_rmq:
    """Lowest common ancestor data structure using a reduction to
       range minimum query
    """
    def __init__(self, graph):
        """builds the structure from a given tree

        :param graph: adjacency matrix of a tree
        :complexity: O(n log n), with n = len(graph)
        """
        n = len(graph)
        dfs_trace = []
        self.last = [None] * n
        to_visit = [(0, 0, None)]            # sommet 0 est la racine
        next = [0] * n
        while to_visit:
            level, node, father = to_visit[-1]
            self.last[node] = len(dfs_trace)
            dfs_trace.append((level, node))
            if next[node] < len(graph[node]) and \
               graph[node][next[node]] == father:
                next[node] += 1
            if next[node] == len(graph[node]):
                to_visit.pop()
            else:
                neighbor = graph[node][next[node]]
                next[node] += 1
                to_visit.append((level + 1, neighbor, node))
        self.rmq = Range_min_query(dfs_trace, (float('inf'), None))

    def query(self, u, v):
        """:returns: the lowest common ancestor of u and v
        :complexity: O(log n)
        """
        lu = self.last[u]
        lv = self.last[v]
        if lu > lv:
            lu, lv = lv, lu
        return self.rmq.range_min(lu, lv + 1)[1]
# snip}


if __name__ == "__main__":
    nodes = list(range(16))
    prec = [u // 2 for u in nodes]
    prec[0] = 0
    LCA = LowestCommonAncestor_by_shortcuts(prec)
    assert LCA.query(9, 9) == 9
    assert LCA.query(9, 0) == 0
    assert LCA.query(0, 0) == 0
    assert LCA.query(0, 1) == 0
    assert LCA.query(1, 1) == 1
    assert LCA.query(4, 11) == 2

    graph = [[1], [0, 2, 9], [1, 3, 5], [2, 4], [3],
             [2, 6, 7, 8], [5], [5], [5], [1]]
    LCA = LowestCommonAncestor_by_rmq(graph)
    assert LCA.query(3, 7) == 2
    assert LCA.query(3, 2) == 2
    assert LCA.query(3, 7) == 2
    assert LCA.query(9, 4) == 1
    assert LCA.query(4, 9) == 1
    assert LCA.query(4, 4) == 4
    assert LCA.query(3, 4) == 3
    assert LCA.query(4, 3) == 3
    assert LCA.query(5, 7) == 5
    assert LCA.query(7, 5) == 5
