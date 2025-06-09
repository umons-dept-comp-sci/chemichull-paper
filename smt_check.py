import argparse
import multiprocessing as mp
import sys
import time
from typing import Any, assert_type

import sympy
import z3

import points
from families import FAMILIES, FDI, GENERAL_CONDS

MIN_CHECK: int = 0
MAX_CHECK: float = float("inf")
INDENT: str = " " * 4
TIMEOUT: int = 0
INTERSECTION_TIMEOUT: int = 10 * 60
DEBUG: bool = False


"""
Defines unsupported operators for sympy to convert in z3
"""
known_functions = sympy.printing.smtlib.SMTLibPrinter._default_settings[
    "known_functions"
]
known_functions[sympy.Mod] = "mod"
known_functions[sympy.floor] = "to_int"
known_functions[sympy.Pow] = "^"

"""
Symbols used by sympy.
"""
ns, ms, m12s, m13s, m33s, l12s, l13s, l33s, r12s, r13s, r33s = sympy.symbols(
    "n m m12 m13 m33 l12 l13 l33 r12 r13 r33", integer=True
)

"""
Symbols used by z3.
"""
n, m, m12, m13, m33, l12, l13, l33, r12, r13, r33 = z3.Ints(
    "n m m12 m13 m33 l12 l13 l33 r12 r13 r33"
)


def get_point(name: str) -> tuple[Any, Any, Any]:
    """
    Small function that calls the right get_R function based on name
    """
    func_name = f"get_R{name}"
    func = getattr(points, func_name)
    if callable(func):
        res = func(ns, ms)
        assert_type(res, tuple[Any, Any, Any])
        return res

    else:
        raise Exception("Function not found")


POINT_NAMES: list[str] = points.points
POINTS_DATA: list[tuple[Any, Any, Any]] = [get_point(p) for p in POINT_NAMES]


def print_debug(indent: int, txt: str):
    if DEBUG:
        now = time.strftime("%H:%M").ljust(len(INDENT * indent))
        print(now, txt, file=sys.stderr)


def check_intersection_validity(
    intersection: dict[Any, Any],
    equalities: list[Any],
    other_facets: list[Any],
    conditions: list[Any],
):
    """
    Checks wheter there exists a pair n and m such that the intersection is
    outside of the polytope while the existential conditions of the polytope are
    satisfied.
    """
    facets = [facet.subs(intersection) for facet in equalities + other_facets]
    z3_facets = z3.parse_smt2_string(sympy.smtlib_code(facets))
    z3_constraints = conditions
    solver = z3.Solver()
    # We check if there exists n and m such that one of the facets is not satisfied but the conditions are.
    # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
    solver.add(z3.And([z3.Not(z3.And([*z3_facets])), *z3_constraints]))
    print_debug(3, "Checking valid intersection")
    invalid = solver.check() == z3.sat
    counter = None
    if invalid:
        mod = solver.model()
        counter = (mod.eval(n), mod.eval(m))
    return invalid, counter


def check_intersection_non_empty(
    intersection: dict[Any, Any], conditions: list[Any]
) -> bool:
    """
    If no invalide pair n,m was found, check whether there exists at least one
    valid pair. That is, whether it is a fractional point (thus invalid) or not.
    """
    solver = z3.Solver()
    solver.add(conditions)
    # Check if there exists n and m such that all three are integers
    for v in [m12s, m13s, m33s]:
        eq = sympy.Eq(v, intersection[v])
        solver.add(z3.parse_smt2_string(sympy.smtlib_code(eq)))
    solver.add(m12 >= 0, m13 >= 0, m33 >= 0)
    print_debug(3, "checking integer")
    return solver.check() == z3.unsat


def check_intersection(
    conditions: list[Any], equalities: list[Any], other_facets: list[Any]
):
    """
    Checks if there exists an intersection between the three chosen facets
    (replaced by equalities) that satisfies all other facets and the polytope conditions.
    """
    # Computes the intersection
    inter = sympy.solve(equalities, m12s, m13s, m33s)
    print(INDENT * 2, "Coordinates: " + str(inter))
    # If no intersection, we just return false
    if inter == []:
        return False, None, None, False
    invalid, counter = check_intersection_validity(
        inter, equalities, other_facets, conditions
    )
    empty = False
    if not invalid:
        empty = check_intersection_non_empty(inter, conditions)
        invalid = empty
    return not invalid, inter, counter, empty


def generate_points_equalities(point, inter):
    """
    Generates equalities with one of the lij or rij variables for each component of the point and the intersection.
    """
    points = []
    for i, pair in enumerate([(l12s, r12s), (l13s, r13s), (l33s, r33s)]):
        eq = z3.parse_smt2_string(
            sympy.smtlib_code(sympy.Eq(point[i], pair[0]), auto_declare=False),
            decls={
                "l12": l12,
                "l13": l13,
                "l33": l33,
                "r12": r12,
                "r13": r13,
                "r33": r33,
                "n": n,
                "m": m,
            },
        )
        points.append(eq[0])
        eq = sympy.smtlib_code(sympy.Eq(inter[i], pair[1]), auto_declare=False)
        eq = z3.parse_smt2_string(
            eq,
            decls={
                "l12": l12,
                "l13": l13,
                "l33": l33,
                "r12": r12,
                "r13": r13,
                "r33": r33,
                "n": n,
                "m": m,
            },
        )
        points.append(eq[0])
    return points


def check_vertex_integer(points, z3_constraints):
    """
    Verifies that a given point corresponds to at least one integer point.

    Returns (True,None) if the point can be integer and False as well as a
    message
    """
    solver = z3.Solver()
    # We check if there exists n and m such that the conditions are satisfied but one of the facets is not satisfied.
    # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
    solver.add(
        l12 == r12,
        l13 == r13,
        l33 == r33,
        l12 >= 0,
        l13 >= 0,
        l33 >= 0,
        r12 >= 0,
        r13 >= 0,
        r33 >= 0,
        *z3_constraints,
        *points,
    )
    print_debug(4, "Checking integer")
    if solver.check() != z3.sat:
        return False, "No integer value"
    else:
        return True, None

def check_vertex_equal(points, z3_constraints):
    """
    Verifies that a given point is equal to the intersection of the three facets
    for each valid order and size given by the conditions.

    Returns (True,None) if the point is equal and False as well as a counter-example otherwise
    """
    solver = z3.Solver()
    solver.add(
        z3.And(
            [
                z3.Not(
                    z3.And(
                        [
                            l12 == r12,
                            l13 == r13,
                            l33 == r33,
                            l12 >= 0,
                            l13 >= 0,
                            l33 >= 0,
                            r12 >= 0,
                            r13 >= 0,
                            r33 >= 0,
                        ]
                    )
                ),
                *z3_constraints,
                *points,
            ]
        )
    )
    print_debug(4, "Checking equality")
    res = solver.check()
    if res == z3.unsat:
        return True, None
    else:
        return False, solver.model()


def check_vertex(point, inter, conds) -> tuple[bool, Any]:
    """
    Verifies that a given point is equal to the intersection of the three facets
    for each valid order and size given by the conditions.

    Returns (True,None) if the point is equal and False as well as a counter-example otherwise
    """
    solver = z3.Solver()
    z3_constraints = conds
    points = generate_points_equalities(point, inter)
    res, msg = check_vertex_integer(points, z3_constraints)
    if not res:
        return False, msg
    return check_vertex_equal(points, z3_constraints)


def check_triplet(
    conds, equalities, other_facets, alls, i, j, k, all_points, set_points
):
    # If they have an intersection that falls inside the polytope we check that at least one point satisfies the facets and the conditions
    error = False
    valid, inter, counter, floating = check_intersection(
        conds, equalities, other_facets
    )
    if valid:
        results = []
        ok = False
        inter = [inter[i] for i in [m12s, m13s, m33s]]
        valid_points = []
        for p, point in enumerate(POINTS_DATA):
            print_debug(3, "Checking point " + POINT_NAMES[p])
            res, msg = check_vertex(point, inter, conds)
            if res:
                print_debug(4, "Valid")
                valid_points.append(POINT_NAMES[p])
                ok = True
            else:
                results.append(msg)
        if not ok:
            error = True
            print("Error for facets", alls[i], alls[j], alls[k])
            print("Intersection not in vertex list:", inter)
            for z, res in enumerate(results):
                print(POINT_NAMES[z], ":", res)
        else:
            key = ", ".join(sorted(valid_points))
            if key not in set_points:
                set_points.add(key)
                all_points.append(valid_points)
            txt = INDENT * 3 + " Points: "
            for p in valid_points:
                txt += p + " "
            print(txt)
        return error, all_points, set_points
    else:
        if floating:
            print(INDENT * 3, "Intersection is not integer")
        else:
            print(INDENT * 3, "Always invalid")
            if counter is not None:
                print(INDENT * 3, f"Example: n={counter[0]}, m={counter[1]}")
            else:
                print(INDENT * 3, "No intersection")
        return error, all_points, set_points


def check_triplet_queue(
    conds, equalities, other_facets, alls, i, j, k, all_points, set_points, queue
):
    res = check_triplet(
        conds, equalities, other_facets, alls, i, j, k, all_points, set_points
    )
    queue.put(res)


def check_triplet_timeout(
    conds, equalities, other_facets, alls, i, j, k, all_points, set_points
):
    if INTERSECTION_TIMEOUT > 0:
        q = mp.SimpleQueue()
        p = mp.Process(
            target=check_triplet_queue,
            args=(
                conds,
                equalities,
                other_facets,
                alls,
                i,
                j,
                k,
                all_points,
                set_points,
                q,
            ),
        )
        p.start()
        p.join(INTERSECTION_TIMEOUT)
        if p.is_alive():
            p.kill()
            p.join()
            q.close()
            print(INDENT * 2, "TIMEOUT")
            return False, all_points, set_points
        else:
            res = q.get()
            q.close()
            return res
    else:
        res = check_triplet(
            conds, equalities, other_facets, alls, i, j, k, all_points, set_points
        )
        return res, all_points, set_points


def check_fam(fam):
    alls = fam[0]
    orig_facets = [FDI[f] for f in alls]
    conds = fam[1] + GENERAL_CONDS
    print(INDENT, "Valid when:", conds)
    set_points = set()
    all_points = []
    error = False
    # For each triplet of facet
    for i in range(len(orig_facets)):
        for j in range(i + 1, len(orig_facets)):
            for k in range(j + 1, len(orig_facets)):
                facets = orig_facets[:]
                equalities = []
                other_facets = []
                other_facets_indices = []
                for index in range(len(facets)):
                    # replace the three by equalities
                    if index == i or index == j or index == k:
                        equalities.append(sympy.Eq(facets[index], 0))
                    else:
                        other_facets.append(facets[index] >= 0)
                        other_facets_indices.append(index)
                facets = equalities + other_facets
                print(f"{INDENT*2} Intersection of {alls[i]}, {alls[j]}, {alls[k]}")
                error, all_points, set_points = check_triplet_timeout(
                    conds,
                    equalities,
                    other_facets,
                    alls,
                    i,
                    j,
                    k,
                    all_points,
                    set_points,
                )
    print(INDENT * 2, "All points:", all_points)
    return not error


# two optional parameters: minimum index and maximum index (default to 0 and 100)
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("MIN", type=int, nargs="?", default=0)
    parser.add_argument("MAX", type=int, nargs="?", default=float("inf"))
    args = parser.parse_args()
    return args.MIN, args.MAX


if __name__ == "__main__":
    MIN_CHECK, MAX_CHECK = parse_args()
    i = 0
    for k in range(len(FAMILIES)):
        i += 1
        if MIN_CHECK <= i <= MAX_CHECK:
            print(f"Fam{i}, {" ".join(FAMILIES[k][0])}")
            p = mp.Process(target=check_fam, args=(FAMILIES[k],))
            p.start()
            if TIMEOUT > 0:
                p.join(TIMEOUT)
            else:
                p.join()
            if p.is_alive():
                p.kill()
                print(INDENT, "TIMEOUT")
