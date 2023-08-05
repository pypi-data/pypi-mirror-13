#!/usr/bin/env python3
# Shortest paths by Dijkstra
# jill-jênn vie et christoph dürr - 2015

try:
    from graph import read_graph, write_graph
    from our_heap import OurHeap
except ImportError:
    from . graph import read_graph, write_graph
    from . our_heap import OurHeap

# snip{
from heapq import heappop, heappush


def dijkstra(graph, weight, source=0, target=None):
    """single source shortest paths by Dijkstra

       :param graph: adjacency list
       :param weight: matrix
       :assumes: weights are non-negative
       :param source: source vertex
       :type source: int
       :param target: if given, stops once distance to target found
       :type target: int

       :returns: distance table, precedence table
       :complexity: `O(|V| + |E|log|V|)`
    """
    n = len(graph)
    assert min((weight[u][v] for u in range(n) for v in graph[u]),
               default=0) >= 0
    prec = [None] * n
    black = [False] * n
    dist = [float('inf')] * n
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        dist_node, node = heappop(heap)       # Le sommet le plus proche
        if not black[node]:
            black[node] = True
            if node == target:
                break
            for neighbor in graph[node]:
                dist_neighbor = dist_node + weight[node][neighbor]
                if dist_neighbor < dist[neighbor]:
                    dist[neighbor] = dist_neighbor
                    prec[neighbor] = node
                    heappush(heap, (dist_neighbor, neighbor))
    return dist, prec
# snip}

'''
# snip{ dijkstra_update_heap
from our_heap import OurHeap

# snip}
'''


# snip{ dijkstra_update_heap
def dijkstra_update_heap(graph, weight, source=0, target=None):
    """single source shortest paths by Dijkstra
       with a heap implementing item updates

       :param graph: adjacency list
       :param weight: matrix
       :assumes: weights are non-negatif and weights are infinite for non edges
       :param source: source vertex
       :type source: int
       :param target: if given, stops once distance to target found
       :type target: int
       :returns: distance table, precedence table
       :complexity: `O(|V| + |E|log|V|)`
    """
    n = len(graph)
    assert min((weight[u][v] for u in range(n) for v in graph[u]),
               default=0) >= 0
    prec = [None] * n
    dist = [float('inf')] * n
    dist[source] = 0
    heap = OurHeap([(dist[node], node) for node in range(n)])
    while heap:
        dist_node, node = heap.pop()       # Le sommet le plus proche
        if node == target:
            break
        for neighbor in graph[node]:
            old = dist[neighbor]
            new = dist_node + weight[node][neighbor]
            if new < old:
                dist[neighbor] = new
                prec[neighbor] = node
                heap.update((old, neighbor), (new, neighbor))
    return dist, prec
# snip}


if __name__ == '__main__':
    for testfile in ['gdw_n5_graph', 'gdw_n5_isolated', 'gdw_n5_unreachable',
                     'gdw_n500_big3', 'gdw_n500_big4', 'gdw_n11348_paris', "guw_n12"]:
        fullpath = "../../data/%s.txt" % testfile
        graph, weight = read_graph(fullpath, directed=False, weighted=True,
                                   default_weight=float('inf'))
        dist, prec = dijkstra(graph, weight)
        # print (dist, prec)
        # print(dijkstra_update_heap(graph, weight))
        assert (dist, prec) == dijkstra_update_heap(graph, weight)
        arc_mark = set((prec[u], u) for u in range(len(graph)))
        arc_mark |= set((u, prec[u]) for u in range(len(graph)))
        if testfile == "guw_n12":
          node_label = ["Seattle", "Minneapolis", "Chicago", "Boston",
                         "San Fransisco", "Los Angeles", "Las Vegas", "Denver",
                         "Dallas", "Wash DC", "Miami", "New York"]
        else:
          node_label = dist
        write_graph("../../data/dijkstra_%s.dot" % testfile, graph,
                    directed=False, arc_label=weight,
                    node_label=node_label, arc_mark=arc_mark)
