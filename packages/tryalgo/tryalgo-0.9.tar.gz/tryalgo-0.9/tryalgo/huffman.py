#!/usr/bin/env python3
# Huffman code
# jill-jenn vie et christoph durr - 2014-2015

from heapq import heappush, heappop


# snip{
def huffman(freq):
    """Huffman code

    :param freq: dictionary with frequencies for each item
    :returns: dictionary with binary code string for each item
    :complexity: O(n log n)
    """
    h = []
    for a in freq:
        heappush(h, (freq[a], a))
    while len(h) > 1:
        (fl, l) = heappop(h)
        (fr, r) = heappop(h)
        heappush(h, (fl + fr, (l, r)))
    code = {}
    extract(code, h[0][1])
    return code


def extract(code, tree, prefix=""):
    if isinstance(tree, tuple):
        l, r = tree
        extract(code, l, prefix + "0")
        extract(code, r, prefix + "1")
    else:
        code[tree] = prefix
# snip}


if __name__ == "__main__":
    assert (huffman({'a': 7, 'b': 7, 'c': 7, 'd': 7}) ==
            {'a': '00', 'c': '10', 'b': '01', 'd': '11'})
    assert (huffman({'a': 40, 'b': 5, 'c': 2, 'd': 1}) ==
            {'a': '1', 'c': '001', 'b': '01', 'd': '000'})
