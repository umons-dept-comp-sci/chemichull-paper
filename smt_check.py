from families import families, FDI
import z3
import sympy
import points

MIN_CHECK = 80
MAX_CHECK = 100

"""
Defines unsupported operators for sympy to convert in z3
"""
known_functions = sympy.printing.smtlib.SMTLibPrinter._default_settings[
    "known_functions"
]
known_functions[sympy.Mod] = "mod"
known_functions[sympy.floor] = "to_int"
known_functions[sympy.Pow] = "^"


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
    m12, m13, m33 = sympy.symbols("m12 m13 m33", integer=True)
    # Computes the intersection
    r = sympy.solve(equalities, m12, m13, m33)
    solver = z3.Solver()
    # replaces m12, m13, m33 with their values in r
    facets = [facet.subs(r) for facet in equalities + other_facets]
    z3_facets = z3.parse_smt2_string(sympy.smtlib_code(facets))
    z3_constraints = conditions
    # We check if there exists n and m such that one of the facets is not satisfied but the conditions are.
    # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
    solver.push()
    solver.add(z3.And([z3.Not(z3.And([*z3_facets])), *z3_constraints]))
    res = solver.check()
    sometimes = False
    if res == z3.sat:
        solver.pop()
        solver.add(z3.And(*z3_facets, *z3_constraints))
        sometimes = solver.check() == z3.sat
    return res == z3.unsat, r, sometimes


def check_vertex(point, inter, conds):
    solver = z3.Solver()
    points = sympy.smtlib_code([sympy.Eq(point[i], inter[i]) for i in range(3)])
    points = z3.parse_smt2_string(points)
    z3_constraints = conds
    # We check if there exists n and m such that the conditions are satisfied but one of the facets is not satisfied.
    # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
    solver.add(z3.And([z3.Not(z3.And(points)), *z3_constraints]))
    res = solver.check()
    if res == z3.unsat:
        return None
    else:
        return solver.model()

def check_sometimes_vertex(point, inter, conds):
    n,m = z3.Ints("n m")
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

def check_fam(fam, index):
    if index < MIN_CHECK or index > MAX_CHECK:
        return True
    alls = fam[0]
    orig_facets = [FDI[f] for f in alls]
    conds = fam[1]
    print("    Valid when:", conds)
    # point_names = fam[2]
    # print("    Vertices: ", point_names)
    # points = [get_point(name) for name in point_names]
    m12, m13, m33 = sympy.symbols("m12 m13 m33", integer=True)

    # For each triplet of facet
    for i in range(len(orig_facets)):
        for j in range(i + 1, len(orig_facets)):
            for k in range(j + 1, len(orig_facets)):
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
                # If they have an intersection that falls inside the polytope we check that at least one point satisfies the facets and the conditions
                valid, inter, sometimes = check_intersection(conds, equalities, other_facets)
                print(
                    f"        Intersection of {alls[i]}, {alls[j]}, {alls[k]}: {inter}"
                )
                if valid:
                    results = []
                    ok = False
                    inter = [inter[i] for i in [m12, m13, m33]]
                    valid_points = []
                    for p, point in enumerate(points_data):
                        res = check_vertex(point, inter, conds)
                        if res is None:
                            valid_points.append(point_names[p])
                            ok = True
                        else:
                            results.append(res)
                    if not ok:
                        print("Error for facets", alls[i], alls[j], alls[k])
                        print("Intersection not in vertex list:", inter)
                        for i, res in enumerate(results):
                            print(point_names[i], ":", res)
                        return False
                    else:
                        print("            ", end="")
                        for p in valid_points:
                            print(p, end=" ")
                        print()
                else:
                    incorrect_facets = find_incorrect_facet(inter, other_facets, equalities, conds, other_facets_indices)
                    if incorrect_facets:
                        print("            Invalid facets:", [alls[i] for i in incorrect_facets])
                    if sometimes:
                        inter = [inter[i] for i in [m12, m13, m33]]
                        sometimes_points = []
                        for p, point in enumerate(points_data):
                            res, mod = check_sometimes_vertex(point, inter, conds)
                            if res:
                                sometimes_points.append(f"{point_names[p]} (n={mod[0]}, m={mod[1]})")
                        if sometimes_points:
                            print("            Sometimes valid for points:", sometimes_points)
                    else:
                        print("            Invalid")
    return True


if __name__ == "__main__":
    i = 0
    for k in range(len(families)):
        i += 1
        print(f"Fam{i}, {" ".join(families[k][0])}")
        if not check_fam(families[k], i):
            print("ERROR")
