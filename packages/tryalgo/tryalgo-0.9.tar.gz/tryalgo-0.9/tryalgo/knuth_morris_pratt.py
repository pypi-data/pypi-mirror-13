#!/usr/bin/env python3
# Find a substring by Knuth-Morris-Pratt
# jill-jênn vie et christoph dürr - 2014-2015

# part d'un code de David Eppstein
try:
    from rabin_karp import rabin_karp_matching
except ImportError:
    from . rabin_karp import rabin_karp_matching

from time import time
from random import randint


# snip{
def knuth_morris_pratt(s, t):
    """Find a substring by Knuth-Morris-Pratt

    :param s: the haystack string
    :param t: the needle string
    :returns: index i such that s[i: i + len(t)] == t, or -1
    :complexity: O(len(s) + len(t))
    """
    assert t != ''
    len_s = len(s)
    len_t = len(t)
    r = [0] * len_t
    j = r[0] = -1
    for i in range(1, len_t):
        while j >= 0 and t[i - 1] != t[j]:
            j = r[j]
        j += 1
        r[i] = j
    j = 0
    for i in range(len_s):
        while j >= 0 and s[i] != t[j]:
            j = r[j]
        j += 1
        if j == len_t:
            return i - len_t + 1
    return -1
# snip}

if __name__ == "__main__":
    for match in [rabin_karp_matching, knuth_morris_pratt]:
        avant = time()
        p = "a" * 1000000 + "b"
        t = "a" * 10000000 + "b"
        assert match(t, p) == len(t) - len(p)
        p = ''.join(map(str, [randint(0, 9) for _ in range(100000)]))
        t = ''.join(map(str, [randint(0, 9) for _ in range(1000000)]))
        assert match(t, p) == -1  # hopefully
        assert match("ab", "a") == 0
        assert match("ab", "b") == 1
        assert match("ab", "c") == -1
        assert match("",   "c") == -1
        print(time() - avant)
