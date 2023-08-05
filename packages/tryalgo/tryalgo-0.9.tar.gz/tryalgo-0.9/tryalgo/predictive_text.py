#!/usr/bin/env python3
# Predictive text for mobile phones
# jill-jenn vie et christoph durr - 2014-2015

__all__ = ["predictive_text"]

# snip{
t9 = "22233344455566677778889999"
#     abcdefghijklmnopqrstuvwxyz   correspondance


def lettre_chiffre(x):
    """:returns: the digit correspondence for letter x"""
    assert 'a' <= x and x <= 'z'
    return t9[ord(x)-ord('a')]


def mot_code(mot):
    """:returns: the digit correspondence for word mot"""
    return ''.join(map(lettre_chiffre, mot))


def predictive_text(dico):
    """Predictive text for mobile phones

    :param dico: associates weights to words from [a-z]*
    :returns: a dictionary associating to words from [2-9]*
             a corresponding word from the dictionary with highest weight
    :complexity: linear in total word length
    """
    freq = {}   # freq[p] = poids total des mots de préfixe p
    for mot, poids in dico:
        prefixe = ""
        for x in mot:
            prefixe += x
            if prefixe in freq:
                freq[prefixe] += poids
            else:
                freq[prefixe] = poids
    #   prop[s] = préfixe à afficher sur s
    prop = {}
    for prefixe in freq:
        code = mot_code(prefixe)
        if code not in prop or freq[prop[code]] < freq[prefixe]:
            prop[code] = prefixe
    return prop


def propose(prop, seq):
    if seq in prop:
        return prop[seq]
    else:
        return "None"
# snip}


if __name__ == "__main__":
    dico = [("another", 5),  ("contest", 6),  ("follow", 3),
            ("give", 13),  ("integer", 6),  ("new", 14),  ("program", 4)]
    prop = predictive_text(dico)
    A = ""
    for seq in ["7764726", "639", "468", "2668437", "7777"]:
        for i in range(len(seq)):
            A += propose(prop, seq[:i + 1]) + " "
    assert A == "p pr pro prog progr progra program n ne new g "\
                "in int c co con cont anoth anothe another p pr None None "
