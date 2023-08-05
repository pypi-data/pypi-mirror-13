#!/usr/bin/env python3
# Fast Exponentiation
# jill-jenn vie et christoph durr - 2014-2015


# snip{
def fast_exponentiation(a, b, q):
    """Compute (a pow b) % q

    :complexity: O(log b)
    """
    assert a >= 0 and b >= 0 and q >= 1
    p = 0               # ne sert qu'à la documentation
    p2 = 1              # 2 ^ p
    ap2 = a % q         # a ^ (2 ^ p)
    result = 1
    while b > 0:
        if p2 & b > 0:  # décomposition bin. de b contient a^(2^p)
            b -= p2
            result = (result * ap2) % q
        p += 1
        p2 *= 2
        ap2 = (ap2 * ap2) % q
    return result
# snip}


if __name__ == "__main__":
    assert fast_exponentiation(1, 23, 1000) == 1
    assert fast_exponentiation(23, 1, 1000) == 23
    assert fast_exponentiation(23, 2, 1000) == 23 * 23
    assert fast_exponentiation(23, 0, 1000) == 1
    assert fast_exponentiation(7, 23, 1000000000) == 80916343
    assert fast_exponentiation(7, 2323474, 1000000000) == 428796849
