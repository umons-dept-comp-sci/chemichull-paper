from full_check import get_families, check_rv_points, NMIN, NMAX, only_modulo
from syseq import FDI
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
    import sympy as sp
    n, m = sp.symbols('n m', integer=True)
    func_name = f"get_R{name}"
    func = getattr(points, func_name)
    if callable(func):
        return func(n, m)
    else:
        raise Exception("Function not found")

def get_fam_cond(f, couples):
    """
    Adapted from Hadrien's code.
    This is basically the same code but returns z3 expressions instead of text
    """
    n, m = z3.Ints('n m')
    res = []
    m_min_s = []
    m_max_s = []
    
    if 'G4' in f:
        m_min_s.append(m > n-1)
        m_max_s.append(m<(3*n/2)-2)
    else:
        m_min_s.append(m>=(3*n/2)-2)
    if 'G5' in f or 'G10' in f or 'G11' in f:
        m_max_s.append(m<(6*n-3)/5)
    else:
        m_min_s.append(m>=(6*n-3)/5)
    if 'G12' in f or 'G13' in f or 'G14' in f:
        m_max_s.append(m<6*n/5)
    else:
        check_m = only_modulo(couples, 2, 4)
        if not (check_m[0] and check_m[1] == 0):
            m_min_s.append(m>=6*n/5)
    if 'G7b' in f:
        m_min_s.append(m>n+1)
    if 'G6' in f:
        if (m>n-1) in m_min_s:
            m_min_s.append(m>n)
        elif 'G16' in f or 'G7' in f or 'G15' in f or 'G17' in f or 'G19' in f or 'G20' in f:
            pass
        else:
            res.append(m!=n)
    if 'G18' in f:
        res.append(m==n)
        m_min_s = []
        m_max_s = []
    if 'G16' in f or 'G7 ' in f:
        res.append(m==n+1)
        m_min_s = []
        m_max_s = []
    if 'G15' in f or 'G17' in f or 'G19' in f or 'G20' in f:
        res.append(m==n-1)
        m_min_s = []
        m_max_s = []
    # In the original code, the "f" was "kk" for these two ifs ?
    if 'G7 ' not in f and 'G7b' not in f and 'G4' in f and not('G6' in f or 'G18' in f):
        res.append(m==n)
        m_min_s = []
        m_max_s = []
    if not 'G5' in f and ('G12' in f or 'G13' in f or 'G14' in f):
        res.append(m==(6*n-(n%5))/5)
        m_min_s = []
        m_max_s = []
    if not (len(m_min_s) == 0 and len(m_max_s) == 0):
        if len(m_min_s) > 0:
            res += m_min_s
        if len(m_max_s) > 0:
            res += m_max_s
    return res

def get_cond_mod(couples, i, mod):
    """
    Adapted from Hadrien's code. Returns z3 expression instead of text.
    """
    n, m = z3.Ints('n m')
    s = n
    if i == 1:
        s = m
    if i == 2:
        s = (m-2*n)
    res = only_modulo(couples, i, mod)
    if res[0]:
        return s%str(mod)==res[1]
    return None

def get_stats(couples):
    """
    Adapted from Hadrien's code. Returns z3 expression instead of text.
    """
    n_z3, m_z3 = z3.Ints('n m')
    if len(couples) == 1:
        return [n_z3 == couples[0][0], m_z3 == couples[0][1]]
    n_min = NMAX
    for c in couples:
        (n, m) = c
        if n < n_min:
            n_min = n
    return [n_z3 >= n_min, m_z3 >= 0]

def get_conds(k, couples):
    """
    Builds the list of conditions for the polytope.
    """
    conds = get_stats(couples)
    if len(couples) > 1:
        conds += [get_cond_mod(couples, 0, 2), get_cond_mod(couples, 1, 3), get_cond_mod(couples, 2, 4)]
        conds += get_fam_cond(k, couples)
    return [cond for cond in conds if cond is not None]

def check_intersection(conditions, equalities, other_facets):
    """
    Checks if there exists an intersection between the three chosen facets
    (replaced by equalities) that satisfies all other facets and the polytope conditions.
    """
    m12, m13, m33 = sympy.symbols('m12 m13 m33', integer=True)
    # Computes the intersection
    r = sympy.solve(equalities, m12, m13, m33)
    import z3
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

# def check_vertex(conditions, facets, p):
#     """
#     Checks that the point p satisfies the facets and the conditions.
#     Three facets have been replaced by equalities to ensure it is an intersection of these three.
#     """
#     import z3
#     solver = z3.Solver()
#     z3_facets = z3.parse_smt2_string(sympy.smtlib_code(facets))
#     z3_constraints = conditions
#     # We check if there exists n and m such that the conditions are satisfied but one of the facets is not satisfied.
#     # Equivalently, for all n and m, either the conditions are not satisfied or all the facets are satisfied.
#     solver.add(z3.And([z3.Not(z3.And(z3_facets)), *z3_constraints]))
#     # print(solver)
#     res = solver.check()
#     if res == z3.unsat:
#         return None
#     else:
#         return solver.model()

def check_vertex_new(point, inter, conds):
    import z3
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
    # print(solver)
    res = solver.check()
    if res == z3.unsat:
        return None
    else:
        return solver.model()

def check_fam(fam, k, index, total):
    if index < MIN_CHECK or index > MAX_CHECK:
        return True
    alls, couples = k.split(), fam[k]
    res = check_rv_points(alls, couples)
    orig_facets = [FDI[f] for f in alls]
    conds = get_conds(k, couples)
    print("    Valid when:", conds)
    point_choice = max(res, key=lambda x: len(res[x]))
    point_names = [v.strip("()").split("=")[0] for v in point_choice.split("+")]
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
                        # point_facets = [
                        #     facet.subs({m12: point[0], m13: point[1], m33: point[2]}) for facet in facets]
                        # print(point_facets)
                        # res = check_vertex(conds, point_facets, point)
                        res = check_vertex_new(point, inter, conds)
                        if res is None:
                            ok = True
                            # print(i,j,k,polytope.facets)
                            # print("ok")
                            break
                        else:
                            results.append(res)
                    if not ok:
                        print("Error for facets", alls[i], alls[j], alls[k])
                        print("Intersection not in vertex list:", inter)
                        for i,res in enumerate(results):
                            print(point_names[i],":",res)
                        # print(i,j,k,polytope.facets)
                        return False
                else:
                    # print(i,j,k,polytope.facets)
                    # print("no valid inter")
                    pass
    return True

if __name__ == '__main__':

    fam = get_families(NMIN, NMAX)
    fam_by_len = {}
    for k in fam:
        l = len(fam[k])
        if l in fam_by_len:
            fam_by_len[l].append(k)
        else:
            fam_by_len[l] = [k]


    total = 0
    for k in fam:
        total += len(fam[k])

    i = 0
    for k in sorted(fam_by_len):
        for kk in fam_by_len[k]:
            i += 1
            print(f"Fam{i}, {kk}")
            if not check_fam(fam, kk, i, total):
                print("ERROR")
