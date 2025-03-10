from sympy import *
from cond import *
import math

m12, m13, m33, n, m = symbols('m12 m13 m33 n m', integer=True)
FDI = {
    'G1': -4*m12 - 3*m13 + m33 - 5*m + 6*n,
    'G2': m12,
    'G3': m13,
    'G4': m12 + m13 - m33 - 3*n + 3*m,
    'G5': m33,
    'G6': 2*m12 + m13 - m33 - 3*n + 3*m - 1,
    'G7': (n-4)*m12 + (n-2)/2 * m13 - (n-4)/2 * m33 + n - 5,
    'G7b': (3*n-2*m)*m12 + (3*n/2 - m + 1) * m13 - (3*n/2 - m) * m33 - 3 * m**2 + (15*n/2 + 1) * m - (9*n**2 + 3*n)/2,
    'G8': -2*m12 - m13 - 4*m/3 + 2*n - Rational(2,3),
    'G9': -m12 - 2*m/3 + n - Rational(2,3),
    'G10': -2*m12 - 2*m13 + m33 - 10*m/3 + 4*n - Rational(2,3),
    'G11': -m12 - m13 + m33 - 5*m/3 + 2*n - Rational(2,3),
    'G12': -3*m12 - 2*m13 + m33 - 15*m/4 + 9*n/2 - Rational(3,4),
    'G13': -m12 + m33 - 5*m/4 + 3*n/2 - Rational(3, 4),
    'G14': -2*m12 - m13 + m33 - 5*m/2 + 3*n - 1,
    'G15': (n-7)*m12 + (n-6)*m13 - (n-4) * m33 -2*n + 14,
    'G16': 2*m12 + 2*m13 - m33 + 1,
    'G17': (n-4)*m12 + (n-4)/2 * m13 - (n-6)/2 * m33 - 2*n + 8,
    'G18': (n-2)*m12 + (n-3)/2 * m13 - (n-1)/2 * m33,
    'G19': (n-9)*m12 + (n-6) * m13 - (n-6) * m33 - 2*n + 18,
    'G20': (2*n-16)*m12 + (2*n - 13) * m13 - (2*n-10) * m33 - 4*n + 32,
    'G21a': 2*m13 - 4*m33,
    'G21b': 4*m13 - 4*m33,
    'G21c': 2*m12 + 5*m13 - 4*m33,
    'G21d': 2*m12 + 8*m13 - 4*m33
}

def get_condition(s):
    if s == 'G1':
        return cond_G1
    if s == 'G2':
        return cond_G2
    if s == 'G3':
        return cond_G3
    if s == 'G4':
        return cond_G4
    if s == 'G5':
        return cond_G5
    if s == 'G6':
        return cond_G6
    if s == 'G7':
        return cond_G7
    if s == 'G7b':
        return cond_G7b
    if s == 'G8':
        return cond_G8
    if s == 'G9':
        return cond_G9
    if s == 'G10':
        return cond_G10
    if s == 'G11':
        return cond_G11
    if s == 'G12':
        return cond_G12
    if s == 'G13':
        return cond_G13
    if s == 'G14':
        return cond_G14
    if s == 'G15':
        return cond_G15
    if s == 'G16':
        return cond_G16
    if s == 'G17':
        return cond_G17
    if s == 'G18':
        return cond_G18
    if s == 'G19':
        return cond_G19
    if s == 'G20':
        return cond_G20
    if s == 'G21a':
        return cond_G21a
    if s == 'G21b':
        return cond_G21b
    if s == 'G21c':
        return cond_G21c
    if s == 'G21d':
        return cond_G21d
        

def get_subs(name):
    subs = set()
    if name == 'G7' or name == 'G16':
        subs.add('n+1')
    if name == 'G15' or name == 'G17' or name == 'G19' or name == 'G20':
        subs.add('n-1')
    if name == 'G18':
        subs.add('n')
    return subs
    
def get_all_subs(alls):
    all_subs = set()
    for k in alls:
        all_subs.update(get_subs(k))
    if len(all_subs) == 0:
        return None
    elif len(all_subs) > 1:
        raise NotImplementedError('More than one substitution') 
    else:
        return all_subs.pop()
    
def display_res(eq1, eq2, eq3, res):
    print(eq1, eq2, eq3,': ', res)

def check_one(eq, alls, couples, verbose = False):
    msg = ''
    for ni, mi in couples:
        try:
            if eq.subs({n: ni, m: mi}) < 0:
                msg = 'Example of violation: when (n,m) = (' + str(ni) + ', ' + str(mi) + '), it gives ' + str(eq.subs({n: ni, m: mi})) + ' that is < 0'
                return False, msg
        except:
            msg = 'NaN for (n,m) = (' + str(ni) + ', ' + str(mi) + ')'
            return False, msg
    return True, msg
  
def check_validity(res, i, j, k, alls, couples, verbose = False):
    acceptable = True
    msg = ''
    for eq in range(len(alls)):
        if eq != i and eq != j and eq != k:
            check, msg_error = check_one(FDI[alls[eq]].subs({m12: res[m12], m13: res[m13], m33: res[m33]}), alls, couples, verbose)
            if not check:   
                msg += 'KO for ' + str(alls[eq] + ' that becomes ' + str(FDI[alls[eq]].subs({m12: res[m12], m13: res[m13], m33: res[m33]})) + ' >= 0 after substition ')
                msg += '\n  ' + msg_error
                acceptable = False
    return acceptable, msg
 
def find_extreme_points(alls, couples, verbose = False): 
    accepted_points = set()  
    
    for i in range(len(alls)):
        for j in range(i+1, len(alls)):
            for k in range(j + 1, len(alls)):
                f1 = FDI[alls[i]]
                f2 = FDI[alls[j]]
                f3 = FDI[alls[k]]
                
                """
                if get_all_subs(alls) != None:
                    s_m = get_all_subs(alls)
                    f1 = f1.subs({m: s_m})
                    f2 = f2.subs({m: s_m})
                    f3 = f3.subs({m: s_m})
                """    
                res = solve([f1, f2, f3], m12, m13, m33, dict=False)
                if (len(res) > 0):
                    if verbose:
                        display_res(alls[i], alls[j], alls[k], res)
                    acc, msg = check_validity(res, i, j, k, alls, couples, verbose)
                    if not acc:
                        if verbose:
                            print('REJECTED:', msg)
                    else:
                        accepted_points.add((res[m12], res[m13], res[m33]))
                else:
                    if verbose:
                        print(alls[i], alls[j], alls[k], ': No solution')
    return accepted_points


def analyse_family(family, couples, union_pts, verbose = False):
    accepted_points = find_extreme_points(family, couples, verbose)
    print('# of points for', ' '.join(family), ':' , len(accepted_points), end=' ')    
    union_pts.update(accepted_points)
    print('(Current total: ' +  str(len(union_pts)) + ')')

def check_redudancy(accepted_points, couples, verbose = False):
    msg = ''
    test_red = True
    msg_real = ''
    merged_points = {}
    
    for c in couples:
        if verbose:
            print('\n','*'*10)
            print(c)
        tot = len(accepted_points)
        real_points = set()
        
        for p in accepted_points:
            sp = (p[0].subs({n: c[0], m: c[1]}), p[1].subs({n: c[0], m: c[1]}), p[2].subs({n: c[0], m: c[1]}))
            real_points.add(sp)
            if verbose:
                print(sp, p)
            if sp in merged_points:
                merged_points[sp].append(p)
            else:
                merged_points[sp] = [p]
        if tot - len(real_points) > 0:
            msg += 'Redundancy for ' + str(c) + ': ' + str(tot - len(real_points)) + '\n'
            test_red = False
            if verbose:
                print(msg) 
        else:
            msg += 'No redundancy for ' + str(c) + '\n' 
        msg_real +=  str(len(real_points)) + str(c) + ' '
    return test_red, msg, msg_real, merged_points
 
if __name__ == '__main__':            
    union_extreme_points = set()
    fam = get_families(10, 15)

    """
    print('Number of families:', len(fam))
    for k in sorted(fam):
        alls, couples = k.split(), fam[k]
    
        analyse_family(alls, couples, union_extreme_points, verbose=False)

        alls, couples = k.split(), fam[k]
    """

    k = 'G1 G2 G3 G4 G7 G13 G16'
    #k = 'G1 G2 G3 G4 G6'

    #if k in fam:
    for k in sorted(fam):
        alls, couples = k.split(), fam[k]
        print(get_all_subs(alls))
        accepted_points = find_extreme_points(alls, couples, False)
        print('# of points for', k, ':' , len(accepted_points), end=' ')
        test_red, msg, nb = check_redudancy(accepted_points, couples, False)
        if not test_red:
            #print(msg)
            print(' # real :', nb)
        else:
            print(' # No redundancy')

    """ 
    print('Union of all extreme points')
    for k in union_extreme_points:
        print('  ', k)
    print('Total number of extreme points: ', len(union_extreme_points))   
    """ 
