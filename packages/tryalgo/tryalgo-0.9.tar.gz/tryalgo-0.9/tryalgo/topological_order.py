#!/usr/bin/env python3
# Topological order
# jill-jenn vie et christoph durr - 2014-2015


# snip{ topological_order_dfs
def topological_order_dfs(graph):
    """Topological sorting by depth first search

    :param graph: adjacency list
    :returns: list of vertices in order
    :complexity: `O(|V|+|E|)`
    """
    n = len(graph)
    order = []
    times_seen = [-1] * n
    for start in range(n):
        if times_seen[start] == -1:
            times_seen[start] = 0
            to_visit = [start]
            while to_visit:
                node = to_visit[-1]
                children = graph[node]
                if times_seen[node] == len(children):
                    to_visit.pop()
                    order.append(node)
                else:
                    child = children[times_seen[node]]
                    times_seen[node] += 1
                    if times_seen[child] == -1:
                        times_seen[child] = 0
                        to_visit.append(child)
    return order[::-1]
# snip}


# snip{
def topological_order(graph):
    """Topological sorting by maintaining indegree

    :param graph: adjacency list
    :returns: list of vertices in order
    :complexity: `O(|V|+|E|)`
    """
    V = range(len(graph))
    indeg = [0 for _ in V]
    for node in V:    # determiner degree entrant
        for neighbor in graph[node]:
            indeg[neighbor] += 1
    Q = [node for node in V if indeg[node] == 0]
    order = []
    while Q:
        node = Q.pop()                # sommet sans arc entrant
        order.append(node)
        for neighbor in graph[node]:
            indeg[neighbor] -= 1
            if indeg[neighbor] == 0:
                Q.append(neighbor)
    return order
# snip}


if __name__ == "__main__":
    for f in [topological_order_dfs, topological_order]:
        assert f([]) == []
        assert f([[]]) == [0]
        assert f([[], [0]]) == [1, 0]
        assert f([[1], []]) == [0, 1]
        assert (f([[1, 5], [2, 3, 5], [3], [4, 5], [5], []]) ==
                [0, 1, 2, 3, 4, 5])
        n = 1000000
        G = [[v for v in range(u + 1, min(u + 10, n))] for u in range(n)]
        assert f(G) == list(range(n))
