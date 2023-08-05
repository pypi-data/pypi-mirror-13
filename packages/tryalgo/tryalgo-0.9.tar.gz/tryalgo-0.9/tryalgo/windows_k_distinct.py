#!/usr/bin/env python3
# All sliding windows containing k distinct elements
# jill-jenn vie et christoph durr - 2014-2015


# snip{
def windows_k_distinct(x, k):
    """All sliding windows containing k distinct elements

    :param x: list
    :yields: all intervals [i,j] with this property
    :complexity: `O(|x|)`
    """
    i = 0
    j = 0
    occ = {xi: 0 for xi in x}
    dist = 0                    # dist := nb z tel que occ[z]>0
    while j < len(x) or dist > k:
        if dist <= k:
            if occ[x[j]] == 0:
                dist += 1
            occ[x[j]] += 1
            j += 1
        else:
            occ[x[i]] -= 1
            if occ[x[i]] == 0:
                dist -= 1
            i += 1
        if dist == k:
            yield (i, j)
# snip}

if __name__ == "__main__":
    L = "abbabacccababaccacab"
    for i, j in windows_k_distinct(L, 2):
        print(L[i:j])
