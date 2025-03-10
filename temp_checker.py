from math import comb
from sympy import *
from z3 import parse_smt2_string
from polytope import myPolytope
from z3_check import z3_simp
from itertools import combinations

m, n, a, b, c = symbols('m n a b c', integer=True)
m12, m13, m33 = symbols('m12 m13 m33', integer=True)
x = symbols("x", integer=True)
y = symbols("y", integer=True)

def check_vertex_new(polytope,vertex):
    point = vertex[0]
    # Find at least three different facets where it's tight
    point_facets = [facet for facet in polytope.facets]
    print(polytope.conditions)
    print(point_facets)
    i = 0
    j = 3
    k = 4
    # for i in range(len(polytope.facets)):
    #     for j in range(i+1, len(polytope.facets)):
    #         for k in range(j+1,len(polytope.facets)):
    facets = polytope.facets[:]
    facets[i] = Eq(facets[i].lhs, facets[i].rhs)
    facets[j] = Eq(facets[j].lhs, facets[j].rhs)
    facets[k] = Eq(facets[k].lhs, facets[k].rhs)
    facets = [facet.subs({m12: point[0], m13: point[1], m33:
                        point[2]}) for facet in facets]
    print("before",i,j,k,facets)
    conds = [cond for cond in polytope.conditions]
    res = facets[:]
    print(res)
    # res = z3_simp([*facets, *conds])
    res = True
    for i in range(len(facets)):
        subres = ask(facets[i],
                     context=polytope.conditions+facets[:i]+facets[i+1:])
        print("facet",facets[i], subres)
        res = res and subres
    # for v in [x,y,n,m]:
    #     # res = solve([*facets, *conds], v)
    #     res = reduce_inequalities(res, v)
    #     print(v, res)
    # for v in [x,y,n,m]:
    #     # res = solve([*facets, *conds], v)
    #     res = reduce_inequalities([*res, *conds], v)
    print(i,j,k,facets, res)
    if res:
        return True
    return False

def check_vertex_old(polytope, vertex):
    # check all equal
    for i in range(len(vertex)-1):
        for j in range(i+1, len(vertex)):
            for coord in range(3):
                if not Eq(vertex[i][coord] - vertex[j][coord],0).subs(n%2,0).subs(m%3,0).doit():
                    print("One of the 'points' is different")
                    return False

    point = vertex[0]
    # Find at least three different facets where its tight
    num = 0
    for facet in polytope.facets:
        old_facet = facet
        facet = facet.subs({m12: point[0], m13: point[1], m33:
                            point[2]}).subs(m%3,0).subs(n%2,0)
        conds = [cond.subs(m%3,0).subs(n%2,0) for cond in polytope.conditions]
        ok = False
        if facet.equals(true):
            ok = True
        elif not facet.equals(false):
            facet = Eq(facet.lhs, facet.rhs)
            # if z3_simp([facet, *polytope.conditions]):
            #     ok = True

            # for v in [n,m]:
            #     facet = reduce_inequalities([facet, *conds], v)
        if ok:
            num += 1
        print(point, facet, old_facet)
    print(num)

def check_intersection(polytope, equalities, other_facets):
    r = solve(equalities, m12, m13, m33)
    # print(r)
    import z3
    solver = z3.Solver()
    facets = [
        facet.subs(r)
        for facet in equalities+other_facets
    ]
    z3_facets = z3.parse_smt2_string(smtlib_code(facets))
    z3_constraints = z3.parse_smt2_string(smtlib_code(polytope.conditions))
    solver.add(z3.And([z3.Not(z3.And([*z3_facets])),*z3_constraints]))
    res = solver.check()
    # if res == z3.sat:
    #     print(solver)
    #     print(solver.model())
    return res == z3.unsat


def check_vertex(polytope, facets, p):
    import z3
    solver = z3.Solver()
    z3_facets = z3.parse_smt2_string(smtlib_code(facets))
    z3_constraints = z3.parse_smt2_string(smtlib_code(polytope.conditions))
    solver.add(z3.And([z3.Not(z3.And(z3_facets)), *z3_constraints]))
    # print(solver)
    res = solver.check()
    # if res == z3.sat:
    #     print(solver.model())
    return res == z3.unsat

def to_equality(facet):
    return Eq(facet.lhs, facet.rhs)

def check_polytope(polytope):
    for i in range(len(polytope.facets)):
        for j in range(i+1, len(polytope.facets)):
            for k in range(j+1,len(polytope.facets)):
                facets = polytope.facets[:]
                equalities = []
                other_facets = []
                for l in range(len(facets)):
                    if l in [i,j,k]:
                        equalities.append(to_equality(facets[l]))
                    else:
                        other_facets.append(facets[l])
                facets = equalities+other_facets
                if check_intersection(polytope, equalities, other_facets):
                    ok = False
                    for point in polytope.vertices[0]:
                        point = point[0]
                        # print(point)
                        point_facets = [
                            facet.subs({m12: point[0], m13: point[1], m33: point[2]}) for facet in facets]
                        # print(point_facets)
                        if check_vertex(polytope, point_facets, point[0]):
                            ok = True
                            # print(i,j,k,polytope.facets)
                            print("ok")
                            break
                    if not ok:
                        # print(i,j,k,polytope.facets)
                        print("ko")
                else:
                    # print(i,j,k,polytope.facets)
                    print("no valid inter")


check_polytope(myPolytope)

# for all triplet of facets, for all points, replace the three facets by
# equalities and check that the inequality system is always True for at least
# one point.
