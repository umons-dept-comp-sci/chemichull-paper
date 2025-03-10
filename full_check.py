from cond import *
import points
from syseq import *

# NMIN = 20 # 5
# NMAX = 35 # 100
NMIN = 5
NMAX = 200
EPS = 10E-10

rv_points = []
for x in dir(points):
    if x.startswith('get_RV'):
        rv_points.append(x)
rv_points.sort()

def check_val_points(p):
    for i in range(3):
        if abs(p[i] - round(p[i])) > EPS:
            return False
        if p[i] < 0:
            return False
    return True

def get_key_rv(t):
    return '+'.join(t)

def get_formatted_list(res):
    t = []
    for k in res:
        t.append('('+ '='.join(res[k]) + ')')
    t.sort()
    return t

def check_rv_points(alls, couples):
    all_res = {}
    for c in couples:
        res = {}
        #print('couple', c)
        for rv in rv_points:
            #print(rv[5:])
            p = points.__dict__[rv](c[0], c[1])
            if check_val_points(p):
                accepted = True
                pp = (round(p[0]), round(p[1]), round(p[2]))
                #print('p', pp)
                stats = [0]*3 # pos, zeros, neg
                for f in alls:
                    val = FDI[f].subs({n: c[0], m: c[1], m12: pp[0], m13: pp[1], m33: pp[2]})
                    #print(val)
                    if val < 0:
                        stats[2] += 1
                    elif abs(val) < EPS:
                        stats[1] += 1
                    else:
                        stats[0] += 1
                if stats[2] > 0:
                    accepted = False
                    #print('  REJECTED BY NEG')
                if stats[1] < 3:
                    accepted = False
                    #print('  REJECTED BY ZERO')
                #print('stat', stats)
                if accepted:
                    if pp in res:
                        res[pp].append(rv[5:])
                    else:
                        res[pp] = [rv[5:]]
            else:
                pass
                #print('  REJECTED BY VAL')
        #print('RES:', res)
        t = get_formatted_list(res)
        this_key = get_key_rv(t)
        if this_key in all_res:
            all_res[this_key].append(c)
        else:
            all_res[this_key] = [c]
        
    return all_res

def check_same_tuple(p1, p2):
    eps = 10E-10
    if abs(p1[0] - p2[0]) > eps:
        return False
    if abs(p1[1] - p2[1]) > eps:
        return False
    if abs(p1[2] - p2[2]) > eps:
        return False
    return True   

def get_m_min(s):
    if '>=floor(3n/2)-2' in s:
        return 'floor(3n/2)-2 ≤ '
    if '>=6n/5' in s:
        return '6n/5 ≤ '
    if '>=(6n-3)/5' in s:
        return '(6n-3)/5 ≤ '
    if '>n+1' in s:
        return 'n + 1 < '
    if '>n' in s:
        return 'n < '
    if '>n-1' in s:
        return 'n - 1 < '
    return None
    
def get_m_max(s):
    if '<=n+1' in s:
        return ' ≤ n + 1'
    if '<(6n-3)/5' in s:
        return ' < (6n-3)/5'
    if '<6n/5' in s:
        return ' < 6n/5'
    if '<floor(3n/2)-2' in s:
        return ' < ⌊3n/2⌋-2'
    return None

def only_modulo(couples, i, mod):
    stats = [0]*mod
    last = 0
    for c in couples:
        term = c[0]
        if i == 1:
            term = c[1]
        if i == 2:
            term = (c[1] - 2*c[0])
        stats[term % mod] += 1
        last = term % mod
    return stats.count(0) == mod - 1, last

def get_cond_mod(couples, i, mod):
    s = 'n'
    if i == 1:
        s = 'm'
    if i == 2:
        s = '(m-2n)'
    res = only_modulo(couples, i, mod)
    if res[0]:
        return ' ∧ '+s+'%'+str(mod)+' = ' + str(res[1])

    return ''
    

def get_fam_cond(f, couples):
    res = ''
    m_min_s = []
    m_max_s = []
    
    if 'G4' in f:
        m_min_s.append('>n-1')
        m_max_s.append('<floor(3n/2)-2')
    else:
        m_min_s.append('>=floor(3n/2)-2')
    if 'G5' in f or 'G10' in f or 'G11' in f:
        m_max_s.append('<(6n-3)/5')
    else:
        m_min_s.append('>=(6n-3)/5')
    if 'G12' in f or 'G13' in f or 'G14' in f:
        m_max_s.append('<6n/5')
    else:
        check_m = only_modulo(couples, 2, 4)
        if not (check_m[0] and check_m[1] == 0):
            m_min_s.append('>=6n/5')
    if 'G7b' in f:
        m_min_s.append('>n+1')
    if 'G6' in f:
        if '>n-1' in m_min_s:
            m_min_s.append('>n')
        elif 'G16' in f or 'G7' in f or 'G15' in f or 'G17' in f or 'G19' in f or 'G20' in f:
            pass
        else:
            res += ' ∧ m≠n'
    if 'G18' in f:
        res += ' ∧ m = n'
        m_min_s = []
        m_max_s = []
    if 'G16' in f or 'G7 ' in f:
        res += ' ∧ m = n+1'
        m_min_s = []
        m_max_s = []
    if 'G15' in f or 'G17' in f or 'G19' in f or 'G20' in f:
        res += ' ∧ m = n-1'
        m_min_s = []
        m_max_s = []
    if 'G7 ' not in kk and 'G7b' not in kk and 'G4' in kk and not('G6' in kk or 'G18' in kk):
        res += ' ∧ m = n'
        m_min_s = []
        m_max_s = []
    if not 'G5' in kk and ('G12' in kk or 'G13' in kk or 'G14' in kk):
        res += ' ∧ m = (6n-(n%5))/5'
        m_min_s = []
        m_max_s = []
    if not (len(m_min_s) == 0 and len(m_max_s) == 0):
        res += ' ∧ '
        if len(m_min_s) > 0:
            res += get_m_min(m_min_s)
        res += 'm'
        if len(m_max_s) > 0:
            res += get_m_max(m_max_s)
    return res

def get_stats(couples):
    if len(couples) == 1:
        return 'Appears only when (n, m) = ' + str(couples[0]) + '\n'
    n_min = NMAX
    for c in couples:
        (n, m) = c
        if n < n_min:
            n_min = n
    return "Appears when n >= " +str(n_min)


def get_biggest_key(res):
    max_k = None
    max_len = 0
    for k in res:
        if len(res[k]) >= max_len:
            max_len = len(res[k])
            max_k = k
    return max_k

def print_info_fam(fam, k, i, total):
        alls, couples = k.split(), fam[k]
        res = check_rv_points(alls, couples)
        nb_vertices = set()
        for x in res:
            nb_vertices.add(len(x.split('+')))
        nb_vert_s = str(nb_vertices)
        if len(nb_vertices) == 1:
            nb_vert_s = str(nb_vertices.pop())
            
        print('Fam%d: #facets=%d #vertices=%s #couples=%d (%.3f%%)' %  (i, k.count('G'), nb_vert_s, len(couples), 100*len(couples)/total))
        print(' ', get_stats(couples), end='')
        if len(fam[k]) > 1:
            print(get_cond_mod(couples, 0, 2), end='')
            print(get_cond_mod(couples, 1, 3), end='')
            print(get_cond_mod(couples, 2, 4), end='')
            print(get_fam_cond(k, couples))
        print('  Facets:', k)
        
        if len(res) > 1:
            max_k = get_biggest_key(res)
            print('  Vertices:')
            for k in res:
                if k != max_k:
                    if len(res[k]) > 5:
                        print('     -> #', len(k.split('+')), ':', ' '.join(k.split('+')), 'when (n, m) =', (res[k][:5] + ['...']), '(appears', len(res[k])-5, 'times more)')
                    else:
                        print('     -> #', len(k.split('+')), ':', ' '.join(k.split('+')), 'when (n, m) =', res[k])
            if len(res[max_k]) > 5:
                print('     -> #', len(max_k.split('+')), ':', ' '.join(max_k.split('+')), 'otherwise (appears', len(res[max_k]), 'times)')
            else:
                print('     -> #', len(max_k.split('+')),':', ' '.join(max_k.split('+')), 'when (n, m) =', res[max_k]) 
        else:
            for k in res:
                print('  Vertices: #', len(k.split('+')),':', ' '.join(k.split('+')))
        print()
   
def print_title(title):
    print('='*len(title))
    print(title)
    print('='*len(title))
    print()  

if __name__ == '__main__':

    fam = get_families(NMIN, NMAX)
    fam_by_len = {}
    for k in fam:
        l = len(fam[k])
        if l in fam_by_len:
            fam_by_len[l].append(k)
        else:
            fam_by_len[l] = [k]

    print('\nThis document contains three sections:')
    print('  1. Description of points')
    print('  2. Description of polytope\'s families')
    print('  3. List of tight points for each facet')

    print('\nRemark. To create this report:')
    print('  - full dimensional polytopes are computed until n =', NMAX)
    total = 0
    for k in fam:
        total += len(fam[k])
    print('  - this makes a total number of couples (n, m) =', total)
    print()

    print_title('1. Description of points')

    file = open('points_description.txt', 'r')
    for l in file:
        print(l, end='')

    print('\n')

    print_title('2. Description of polytope\'s families')

    focus = 'G7b'

    i = 0
    for k in sorted(fam_by_len):
        for kk in fam_by_len[k]:
            i += 1
            #if not 'G5' in kk and ('G12' in kk or 'G13' in kk or 'G14' in kk):
            #    print_info_fam(fam, kk, i, total)
            print_info_fam(fam, kk, i, total)

    print_title('3. List of tight points for each facet')

    print("-> Remark: tighness is checked only when specific conditions on n, m for a given facet are satisfied")

    always_points = {}


    for k in FDI:
       print('Facet', k, ':', FDI[k], '>= 0')
       always = []
       sometimes = []
       for rv in rv_points:
           accepted = []
           rejected = []
           for ni in range(5, NMAX):
               max_m = round(math.ceil(3*ni/2)-2)
               for mi in range(ni-1, max_m + 1):
                   if full_cond(ni, mi) and get_condition(k)(ni, mi):
                       p = points.__dict__[rv](ni, mi)
                       if check_val_points(p):
                           val = FDI[k].subs({n: ni, m: mi, m12: round(p[0]), m13: round(p[1]), m33: round(p[2])})
                           if abs(val) < EPS:
                               accepted.append((ni, mi))
                           else:
                               rejected.append((ni, mi))
           #print('  ', rv[5:], ':', accepted)
           if len(rejected) == 0:
               always.append(rv[5:])
               if rv[5:] in always_points:
                   always_points[rv[5:]].append(k)
               else:
                   always_points[rv[5:]] = [k]
               #print(' ', rv[5:], 'is always tight')
               #print(accepted)
           if len(accepted) == 0:
               pass
               #print(' ', rv[5:], 'is never tight')
           if len(accepted) > 0 and len(rejected) > 0:
               sometimes.append(rv[5:])
               #print(' ', rv[5:], 'is tight when', accepted)
               #print(' ', rv[5:], 'is NOT tight when', rejected)  
       print('  Always tight:', ' '.join(always))
       if len(sometimes) > 0:
           print('  Sometimes tight:', ' '.join(sometimes))
       print()
       
    for p in sorted(always_points):
       print('Point', p, 'is always tight for', always_points[p])