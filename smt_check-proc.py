from families import FDI, FAMILIES, GENERAL_CONDS
import z3
import sympy
import points

import sys
import argparse
import time

import multiprocessing as mp

MIN_CHECK = 43
MAX_CHECK = 100
INDENT = " " * 4
TIMEOUT = None
INTERSECTION_TIMEOUT = 10 * 60
DEBUG = True


def print_debug(indent, txt):
    if DEBUG:
        now = time.strftime("%H:%M").ljust(len(INDENT * indent))
        print(now, txt, file=sys.stderr)


"""
Defines unsupported operators for sympy to convert in z3
"""
known_functions = sympy.printing.smtlib.SMTLibPrinter._default_settings[
    "known_functions"
]
known_functions[sympy.Mod] = "mod"
known_functions[sympy.floor] = "to_int"
known_functions[sympy.Pow] = "^"


def print_Pow(self, expr):
    power = expr.exp
    div = False
    if power < 0:
        div = True
        power *= -1
    res = ""
    if power == 0:
        res = "1"
    val1 = self.doprint(expr.args[0])
    res = val1
    power -= 1
    while power > 0:
        res = f"(* {val1} {res})"
        power -= 1
    if div:
        return f"(/ 1 {res})"
    else:
        return res


def print_Mul(self, expr):
    if isinstance(expr.args[0], sympy.Rational) and not isinstance(
        expr.args[1], sympy.Rational
    ):
        arg = self.doprint(expr.args[1])
        rat = expr.args[0]
        return f"(div (* {rat.numerator} {arg}) {rat.denominator})"
    elif not isinstance(expr.args[0], sympy.Rational) and isinstance(
        expr.args[1], sympy.Rational
    ):
        arg = self.doprint(expr.args[0])
        rat = expr.args[1]
        return f"(div (* {rat.numerator} {arg}) {rat.denominator})"
    else:
        return f"(* {self.doprint(expr.args[0])} {self.doprint(expr.args[1])})"


# setattr(sympy.printing.smtlib.SMTLibPrinter, "_print_Pow", print_Pow)
# setattr(sympy.printing.smtlib.SMTLibPrinter, "_print_Mul", print_Mul)


def get_point(name):
    """
    Small function that calls the right get_R function based on name
    """
    n, m = sympy.symbols("n m", integer=True)
    func_name = f"get_R{name}"
    func = getattr(points, func_name)
    if callable(func):
        return func(n, m)
    else:
        raise Exception("Function not found")


point_names = points.points
points_data = [get_point(p) for p in point_names]


def check_intersection(conditions, equalities, other_facets):
    """
    Checks if there exists an intersection between the three chosen facets
    (replaced by equalities) that satisfies all other facets and the polytope conditions.
    """
    m12s, m13s, m33s = sympy.symbols("m12 m13 m33", integer=True)
    # Computes the intersection
    r = sympy.solve(equalities, m12s, m13s, m33s)
    print(INDENT * 2, "Coordinates: " + str(r))
    # If no intersection, we just return false
    if r == []:
        return False, None, False, None, False
    solver = z3.Solver()
    facets = [facet.subs(r) for facet in equalities + other_facets]
    z3_facets = z3.parse_smt2_string(sympy.smtlib_code(facets))
    z3_constraints = conditions
    # We check if there exists n and m such that one of the facets is not satisfied but the conditions are.
    # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
    solver.push()
    solver.add(z3.And([z3.Not(z3.And([*z3_facets])), *z3_constraints]))
    print_debug(3, "Checking valid intersection")
    print(solver)
    res = solver.check()
    counter = None
    sometimes = False
    n, m, m12, m13, m33 = z3.Ints("n m m12 m13 m33")
    if res == z3.sat:
        mod = solver.model()
        counter = (mod.eval(n), mod.eval(m))
    #     solver.pop()
    #     solver.add(z3.And(*z3_facets, *z3_constraints))
    #     sometimes = solver.check() == z3.sat
    solver.pop()
    if res == z3.unsat:
        # replaces m12, m13, m33 with their values in r
        solver.push()
        solver.add(conditions)
        # Check if there exists n and m such that all three are integers
        for v in [m12s, m13s, m33s]:
            eq = sympy.Eq(v, r[v])
            solver.add(z3.parse_smt2_string(sympy.smtlib_code(eq)))
        solver.add(m12 >= 0, m13 >= 0, m33 >= 0)
        # print(solver)
        print_debug(3, "checking integer")
        # print(solver)
        if solver.check() == z3.unsat:
            return False, r, False, None, True
        solver.pop()
    return res == z3.unsat, r, sometimes, counter, False


def check_vertex(point, inter, conds):
    # print(point, inter)
    l12, l13, l33, r12, r13, r33, n, m = z3.Ints("l12 l13 l33 r12 r13 r33 n m")
    l12s, l13s, l33s, r12s, r13s, r33s = sympy.symbols(
        "l12 l13 l33 r12 r13 r33", integer=True
    )
    solver = z3.Solver()
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
    # print(points)
    # points = z3.parse_smt2_string(sympy.smtlib_code([sympy.Eq(point[i], inter[i]) for i in range(3)]))
    z3_constraints = conds
    # We check if there exists n and m such that the conditions are satisfied but one of the facets is not satisfied.
    # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
    solver.push()
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
    # print(solver)
    if solver.check() != z3.sat:
        return "No integer value"
    solver.pop()
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
    # solver.add(l12 >= 0, r12 >= 0)
    # solver.add(l13 >= 0, r13 >= 0)
    # solver.add(l33 >= 0, r33 >= 0)
    print_debug(4, "Checking equality")
    # print(solver)
    res = solver.check()
    if res == z3.unsat:
        return None
    else:
        # print(solver.model())
        return solver.model()


def check_sometimes_vertex(point, inter, conds):
    n, m = z3.Ints("n m")
    solver = z3.Solver()
    points = sympy.smtlib_code([sympy.Eq(point[i], inter[i]) for i in range(3)])
    points = z3.parse_smt2_string(points)
    z3_constraints = conds
    solver.add(z3.And([*points, *z3_constraints]))
    res = solver.check()
    if res == z3.unsat:
        return False, None
    mod = solver.model()
    return True, (mod.eval(n), mod.eval(m))


def find_incorrect_facet(inter, facets, equalities, conds, other_facets_indices):
    if inter is None:
        return []
    solver = z3.Solver()
    # replaces m12, m13, m33 with their values in r
    r_facets = [facet.subs(inter) for facet in facets]
    r_equalities = [eq.subs(inter) for eq in equalities]
    z3_facets = z3.parse_smt2_string(sympy.smtlib_code(r_facets))
    z3_equalities = z3.parse_smt2_string(sympy.smtlib_code(r_equalities))
    z3_constraints = conds
    # We check if there exists n and m such that one of the facets is not satisfied but the conditions are.
    # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
    incorrect_facets = []
    for i, facet in enumerate(z3_facets):
        solver.push()
        solver.add(z3.And([z3.Not(facet), *z3_equalities, *z3_constraints]))
        if solver.check() == z3.unsat:
            incorrect_facets.append(other_facets_indices[i])
        solver.pop()
    return incorrect_facets


def check_triplet(
    conds, equalities, other_facets, alls, i, j, k, all_points, set_points
):
    # If they have an intersection that falls inside the polytope we check that at least one point satisfies the facets and the conditions
    error = False
    m12, m13, m33 = sympy.symbols("m12 m13 m33", integer=True)
    valid, inter, sometimes, counter, floating = check_intersection(
        conds, equalities, other_facets
    )
    if valid:
        results = []
        ok = False
        inter = [inter[i] for i in [m12, m13, m33]]
        valid_points = []
        for p, point in enumerate(points_data):
            print_debug(3, "Checking point " + point_names[p])
            res = check_vertex(point, inter, conds)
            if res is None:
                valid_points.append(point_names[p])
                ok = True
            else:
                results.append(res)
        if not ok:
            error = True
            print("Error for facets", alls[i], alls[j], alls[k])
            print("Intersection not in vertex list:", inter)
            for z, res in enumerate(results):
                print(point_names[z], ":", res)
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
        incorrect_facets = []
        # incorrect_facets = find_incorrect_facet(inter, other_facets, equalities, conds, other_facets_indices)
        if not sometimes:
            if floating:
                print(INDENT * 3, "Intersection is not integer")
            else:
                print(INDENT * 3, "Always invalid")
                if counter is not None:
                    print(INDENT * 3, f"Example: n={counter[0]}, m={counter[1]}")
                else:
                    print(INDENT * 3, "No intersection")
        else:
            inter = [inter[i] for i in [m12, m13, m33]]
            sometimes_points = []
            for p, point in enumerate(points_data):
                res, mod = check_sometimes_vertex(point, inter, conds)
                if res:
                    sometimes_points.append(
                        f"{point_names[p]} (n={mod[0]}, m={mod[1]})"
                    )
            print(INDENT * 3, "Sometimes valid for points:", sometimes_points)
            print(INDENT * 3, f"Not when n={counter[0]}, m={counter[1]}")
        if incorrect_facets:
            print(INDENT * 3, "Invalid facets:", [alls[i] for i in incorrect_facets])
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


def check_fam(fam, index):
    alls = fam[0]
    orig_facets = [FDI[f] for f in alls]
    conds = fam[1] + GENERAL_CONDS
    print(INDENT, "Valid when:", conds)
    # point_names = fam[2]
    # print("    Vertices: ", point_names)
    # points = [get_point(name) for name in point_names]
    set_points = set()
    all_points = []
    error = False
    # For each triplet of facet
    for i in range(len(orig_facets)):
        for j in range(i + 1, len(orig_facets)):
            for k in range(j + 1, len(orig_facets)):
                i = 0
                j = 5
                k = 7
                facets = orig_facets[:]
                equalities = []
                other_facets = []
                other_facets_indices = []
                for l in range(len(facets)):
                    # replace the three by equalities
                    if l in [i, j, k]:
                        equalities.append(sympy.Eq(facets[l], 0))
                    else:
                        other_facets.append(facets[l] >= 0)
                        other_facets_indices.append(l)
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
                sys.exit(1)
    print(INDENT * 2, "All points:", all_points)
    return not error


# two optional parameters: minimum index and maximum index (default to 0 and 100)
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("MIN", type=int, nargs="?", default=0)
    parser.add_argument("MAX", type=int, nargs="?", default=100)
    args = parser.parse_args()
    return args.MIN, args.MAX


if __name__ == "__main__":
    MIN_CHECK, MAX_CHECK = parse_args()
    i = 0
    for k in range(len(FAMILIES)):
        i += 1
        if MIN_CHECK <= i <= MAX_CHECK:
            print(f"Fam{i}, {" ".join(FAMILIES[k][0])}")
            p = mp.Process(target=check_fam, args=(FAMILIES[k], i))
            p.start()
            p.join(TIMEOUT)
            if p.is_alive():
                p.kill()
            # if not check_fam(FAMILIES[k], i):
            #     print("ERROR")
