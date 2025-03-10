from families import families, FDI
import z3
import sympy
import points

MIN_CHECK = 0
MAX_CHECK = 200

"""
Defines unsupported operators for sympy to convert in z3
"""
known_functions = sympy.printing.smtlib.SMTLibPrinter._default_settings["known_functions"]
known_functions[sympy.Mod] = "mod"
known_functions[sympy.floor] = "to_int"
known_functions[sympy.Pow] = "^"


def get_point(name):
    """
    Small function that calls the right get_R function based on name
    """
    n, m = sympy.symbols('n m', integer=True)
    func_name = f"get_R{name}"
    func = getattr(points, func_name)
    if callable(func):
        return func(n, m)
    else:
        raise Exception("Function not found")

def check_intersection(conditions, equalities, other_facets):
    """
    Checks if there exists an intersection between the three chosen facets
    (replaced by equalities) that satisfies all other facets and the polytope conditions.
    """
    m12, m13, m33 = sympy.symbols('m12 m13 m33', integer=True)
    # Computes the intersection
    r = sympy.solve(equalities, m12, m13, m33)
    solver = z3.Solver()
    # replaces m12, m13, m33 with their values in r
    facets = [
        facet.subs(r)
        for facet in equalities+other_facets
    ]
    z3_facets = z3.parse_smt2_string(sympy.smtlib_code(facets))
    z3_constraints = conditions
    # We check if there exists n and m such that one of the facets is not satisfied but the conditions are.
    # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
    solver.add(z3.And([z3.Not(z3.And([*z3_facets])),*z3_constraints]))
    res = solver.check()
    if res == z3.unsat:
        return r
    else:
        return None

def check_vertex(point, inter, conds):
    solver = z3.Solver()
    points = sympy.smtlib_code([
        sympy.Eq(point[i],inter[i])
        for i in range(3)
    ])
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

def check_fam(fam, index):
    if index < MIN_CHECK or index > MAX_CHECK:
        return True
    alls = fam[0]
    orig_facets = [FDI[f] for f in alls]
    conds = fam[1]
    print("    Valid when:", conds)
    point_names = fam[2]
    print("    Vertices: ", point_names)
    points = [get_point(name) for name in point_names]
    m12, m13, m33 = sympy.symbols('m12 m13 m33', integer=True)

    # For each triplet of facet
    for i in range(len(orig_facets)):
        for j in range(i+1, len(orig_facets)):
            for k in range(j+1,len(orig_facets)):
                facets = orig_facets[:]
                equalities = []
                other_facets = []
                for l in range(len(facets)):
                    # replace the three by equalities
                    if l in [i,j,k]:
                        equalities.append(sympy.Eq(facets[l],0))
                    else:
                        other_facets.append(facets[l] >= 0)
                facets = equalities+other_facets
                # If they have an intersection that falls inside the polytope we check that at least one point satisfies the facets and the conditions
                inter = check_intersection(conds, equalities, other_facets)
                if inter is not None:
                    results = []
                    ok = False
                    inter = [inter[i] for i in [m12, m13, m33]]
                    for point in points:
                        res = check_vertex(point, inter, conds)
                        if res is None:
                            ok = True
                            break
                        else:
                            results.append(res)
                    if not ok:
                        print("Error for facets", alls[i], alls[j], alls[k])
                        print("Intersection not in vertex list:", inter)
                        for i,res in enumerate(results):
                            print(point_names[i],":",res)
                        return False
                else:
                    pass
    return True

if __name__ == '__main__':
    i = 0
    for k in range(len(families)):
        i += 1
        print(f"Fam{i}, {" ".join(families[k][0])}")
        if not check_fam(families[k], i):
            print("ERROR")
