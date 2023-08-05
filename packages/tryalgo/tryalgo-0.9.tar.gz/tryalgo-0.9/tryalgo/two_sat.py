#!/usr/bin/env python3
# Solving 2-SAT boolean formulas
# jill-jenn vie et christoph durr - 2015

from random import randint
from sys import path
try:
    from strongly_connected_components import tarjan
except ImportError:
    from . strongly_connected_components import tarjan


# snip{
def _vertex(lit):  # codage sommet pour un littéral donné
    if lit > 0:
        return 2 * (lit - 1)
    else:
        return 2 * (-lit - 1) + 1


def two_sat(formula):
    """Solving a 2-SAT boolean formula

    :param formula: list of clauses, a clause is pair of literals
                    over X1,...,Xn for some n.
                    a literal is an integer, for example -1 = not X1, 3 = X3
    :returns: table with boolean assignment satisfying the formula or None
    :complexity: linear
    """
    #                                   -- n est le nombre de variables
    n = max(abs(clause[p]) for p in (0, 1) for clause in formula)
    graph = [[] for node in range(2 * n)]
    for x, y in formula:                           # x or y
        graph[_vertex(-x)].append(_vertex(y))      # -x => y
        graph[_vertex(-y)].append(_vertex(x))      # -y => x
    sccp = tarjan(graph)
    comp_id = [None] * (2 * n)           # pour chaque nœud l'id. de sa comp.
    affectations = [None] * (2 * n)
    for component in sccp:
        rep = min(component)             # représentation de la composante
        for vtx in component:
            comp_id[vtx] = rep
            if affectations[vtx] == None:
                affectations[vtx] = True
                affectations[vtx ^ 1] = False    # littéral complémentaire
    for i in range(n):
        if comp_id[2 * i] == comp_id[2 * i + 1]:
            return None                          # formule insatisfiable
    return affectations[::2]
# snip}

if __name__ == "__main__":
    def instance_aleatoire(nb_variables, nb_clauses):
        clauses = []
        for _ in range(nb_clauses):
            x = 1 - 2 * randint(0, 1) * randint(1, nb_variables)
            y = 1 - 2 * randint(0, 1) * randint(1, nb_variables)
            clauses.append((x, y))
        return clauses

    def check(formula, affectations):
        for x, y in formula:
            if x > 0:
                vx = affectations[x - 1]
            else:
                vx = not affectations[-x - 1]
            if y > 0:
                vy = affectations[y - 1]
            else:
                vy = not affectations[-y - 1]
            assert vx or vy

    def verify(formula, solution):
        affectations = two_sat(formula)
        if affectations is None:
            assert not solution
        elif not solution:
            assert not affectations
        else:
            check(formula, affectations)

    verify([(2, 2)], True)
    verify([(-1, 1)], True)

    verify([[2, -1], [-3, -3], [3, -2], [2, 2]], False)
    verify([[3, -2], [3, 2], [2, -2], [-1, -1]], True)
    verify([(-1, 2), (-1, 3), (-2, -1), (-2, 3)], True)
    verify([(-1, 2), (-2, -1), (1, 3), (-3, 4), (-3, 2), (-4, 1)], False)
    for _ in range(10):
        formula = instance_aleatoire(100000, 100000)
        aff = two_sat(formula)
        if aff:
            check(formula, aff)
