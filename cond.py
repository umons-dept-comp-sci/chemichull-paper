import math

def full_cond(n, m):
    if (n, m) == (5, 5):
        return True
    elif n >= 6:
        max_m = min(math.ceil(3*n/2) - 2, n*(n-1) // 2)
        return m <= max_m
    else:
        return False
    
def display_table():
    print('n/m|  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18')
    print('---+---------------------------------------------------------')
    for n in range(3, 30):
        print('%2d |' % n, end='')
        blanks = ' ' * (n-1) * 3
        print(blanks, end='')
        max_m = min(math.floor(3*n/2), n*(n-1) // 2)
        for m in range(n-1, max_m + 1):
            print('%3d' % count_facets(n,m), end='')
        print()

def cond_G1(n, m):
    if (n, m) in [(5, 5), (6, 5)]:
        return False
    else:
        return True
    
def cond_G2(n, m):
    if (n, m) in [(6, 5), (7, 6), (8, 7), (9, 8)]:
        return False
    else:
        return True
    
def cond_G3(n, m):
    if (n, m) in [(5, 5), (6, 5), (6, 6), (7, 6), (8, 7), (9, 8)]:
        return False
    else:
        return True
    
def cond_G4(n, m):
    if n >= 8:
        return n-1 < m and m < math.floor(3*n/2) - 2
    else:
        return False
    
def cond_G5(n, m):
    return m < (6*n - 3)/5

def cond_G6(n, m):
    return n % 2 == 1 and m != n

def cond_G7(n, m):
    return n % 2 == 0 and m == n + 1

def cond_G7b(n, m):
    return n % 2 == 0 and n + 2 <= m

def cond_G8(n, m):
    if (n, m) == (8, 10):
        return True
    elif n >= 9:
        return (n % 3 == 1 and (m-n) % 3 == 0) or (n % 3 == 0 and (m-n) % 3 == 1) or (n % 3 == 2 and (m-n) % 3 == 2)
    else:
        return False
    
def cond_G9(n, m):
    if (n, m) == (9, 8):
        return False
    elif n >= 7:
        return (n % 3 == 1 and (m-n) % 3 == 1) or (n % 3 == 0 and (m-n) % 3 == 2) or (n % 3 == 2 and (m-n) % 3 == 0)
    else:
        return False    

def cond_G10(n, m):
    if m < (6*n-3)/5:
        return (n % 3 == 1 and (m-n) % 3 == 0) or (n % 3 == 0 and (m-n) % 3 == 1) or (n % 3 == 2 and (m-n) % 3 == 2)
    else:
        return False  

def cond_G11(n, m):
    if m < (6*n-3)/5:
        return (n % 3 == 1 and (m-n) % 3 == 1) or (n % 3 == 0 and (m-n) % 3 == 2) or (n % 3 == 2 and (m-n) % 3 == 0)
    else:
        return False

def cond_G12(n, m):
    mn_cond = (n % 4 == 0 and (m-n) % 4 == 3) or (n % 4 == 1 and (m-n) % 4 == 0) or (n % 4 == 2 and (m-n) % 4 == 1) or (n % 4 == 3 and (m-n) % 4 == 2)
    return n >= 6 and mn_cond and m < (6*n) / 5

def cond_G13(n, m):
    mn_cond = (n % 4 == 0 and (m-n) % 4 == 1) or (n % 4 == 1 and (m-n) % 4 == 2) or (n % 4 == 2 and (m-n) % 4 == 3) or (n % 4 == 3 and (m-n) % 4 == 0)
    return n >= 7 and mn_cond and m < (6*n) / 5

def cond_G14(n, m):
    mn_cond = (n % 4 == 0 and (m-n) % 4 == 2) or (n % 4 == 1 and (m-n) % 4 == 3) or (n % 4 == 2 and (m-n) % 4 == 0) or (n % 4 == 3 and (m-n) % 4 == 1)
    return mn_cond and m < (6*n) / 5

def cond_G14val(n, m):
    mn_cond = (n % 4 == 0 and (m-n) % 4 == 2) or (n % 4 == 1 and (m-n) % 4 == 3) or (n % 4 == 2 and (m-n) % 4 == 0) or (n % 4 == 3 and (m-n) % 4 == 1)
    if (n, m) == (4, 5):
        return False
    if (n, m) in [(3, 3), (4, 4)]:
        return True
    elif m > (6*n)/5:
        return True
    elif n >= 5 and mn_cond:
        return True
    return False


def cond_G15(n, m):
    return n >= 6 and m == n-1

def cond_G16(n, m):
    if (n, m) == (6, 7):
        return False # G16 is true but is equivalent to G7 for (6, 7)   
    return n >= 5 and m == n+1

def cond_G17(n, m):
    return n >= 6 and n % 2 == 0 and m == n - 1

def cond_G18(n, m):
        return n >= 7 and n % 2 == 1 and m == n

def cond_G19(n, m):
    return n >= 9 and n % 3 == 0 and m == n - 1

def cond_G20(n, m):
    return n >= 8 and n % 3 == 2 and m == n - 1

def cond_G21a(n, m):
    return (n, m) == (5, 5)

def cond_G21b(n, m):
    return (n, m) == (6, 6)

def cond_G21c(n, m):
    return (n, m) == (7, 7)

def cond_G21d(n, m):
    return (n, m) == (8, 8)

def displayFam(fam, k, verbose):
    nb = k.count('G')
    print('  ', k[:], '(', len(fam[k]), '):', end='')
    if verbose:
        for n, m in fam[k]:
            print('(', n, m, ')', end='')
    print()

def count_facets(n, m):
    if not full_cond(n, m):
        return -1
    else:
        cnt = 0
        if cond_G1(n, m):
            cnt += 1
        if cond_G2(n, m):        
            cnt += 1
        if cond_G3(n, m):
            cnt += 1
        if cond_G4(n, m):
            cnt += 1
        if cond_G5(n, m):
            cnt += 1
        if cond_G6(n, m):
            cnt += 1
        if cond_G7(n, m):
            cnt += 1
        if cond_G7b(n, m):
            cnt += 1
        if cond_G8(n, m):
            cnt += 1
        if cond_G9(n, m):
            cnt += 1
        if cond_G10(n, m):
            cnt += 1
        if cond_G11(n, m):
            cnt += 1
        if cond_G12(n, m):
            cnt += 1
        if cond_G13(n, m):
            cnt += 1
        if cond_G14(n, m):
            cnt += 1
        if cond_G15(n, m):
            cnt += 1
        if cond_G16(n, m):
            cnt += 1
        if cond_G17(n, m):
            cnt += 1
        if cond_G18(n, m):
            cnt += 1
        if cond_G19(n, m):
            cnt += 1
        if cond_G20(n, m):
            cnt += 1
        if cond_G21a(n, m):
            cnt += 1
        if cond_G21b(n, m):
            cnt += 1
        if cond_G21c(n, m):
            cnt += 1
        if cond_G21d(n, m):
            cnt += 1
        
        return cnt

def display_facets(n, m):
    s = ''
    if cond_G1(n, m):
        s += 'G1'
    if cond_G2(n, m):
        s += 'G2'   
    if cond_G3(n, m):
        s += 'G3'
    if cond_G4(n, m):
        s += 'G4'
    if cond_G5(n, m):
        s += 'G5'
    if cond_G6(n, m):
        s += 'G6'
    if cond_G7(n, m):
        s += 'G7'
    if cond_G7b(n, m):
        s += 'G7b'
    if cond_G8(n, m):
        s += 'G8'
    if cond_G9(n, m):
        s += 'G9'
    if cond_G10(n, m):
        s += 'G10'
    if cond_G11(n, m):
        s += 'G11'
    if cond_G12(n, m):
        s += 'G12'
    if cond_G13(n, m):
        s += 'G13'
    if cond_G14(n, m):
        s += 'G14'
    if cond_G15(n, m):
        s += 'G15'
    if cond_G16(n, m):
        s += 'G16'
    if cond_G17(n, m):
        s += 'G17'
    if cond_G18(n, m):
        s += 'G18'
    if cond_G19(n, m):
        s += 'G19'
    if cond_G20(n, m):
        s += 'G20'
    if cond_G21a(n, m):
        s += 'G21a'
    if cond_G21b(n, m):
        s += 'G21b'
    if cond_G21c(n, m):
        s += 'G21c'
    if cond_G21d(n, m):
        s += 'G21d'
    print(s)
  
def get_families(n_min = 6, n_max = 100, m_step = -2, n_step = 1, diag = False, verbose = False):
    fam = {}

    for n in range(n_min, n_max + 1, n_step):
        if verbose: 
            print('n =', n, end=': ')
        max_m = round(math.ceil(3*n/2)-2)
        if m_step > -2: # -2 means no limit on m
            max_m = n + m_step
            
        min_m = n - 1
        if diag:
            min_m = max_m
        for m in range(min_m, max_m + 1):
            if full_cond(n, m):
                s = ''
                if cond_G1(n, m):
                    s += 'G1 '
                if cond_G2(n, m):
                    s += 'G2 '   
                if cond_G3(n, m):
                    s += 'G3 '
                if cond_G4(n, m):
                    s += 'G4 '
                if cond_G5(n, m):
                    s += 'G5 '
                if cond_G6(n, m):
                    s += 'G6 '
                if cond_G7(n, m):
                    s += 'G7 '
                if cond_G7b(n, m):
                    s += 'G7b '
                if cond_G8(n, m):
                    s += 'G8 '
                if cond_G9(n, m):
                    s += 'G9 '
                if cond_G10(n, m):
                    s += 'G10 '
                if cond_G11(n, m):
                    s += 'G11 '
                if cond_G12(n, m):
                    s += 'G12 '
                if cond_G13(n, m):
                    s += 'G13 '
                if cond_G14(n, m):
                    s += 'G14 '
                if cond_G15(n, m):
                    s += 'G15 '
                if cond_G16(n, m):
                    s += 'G16 '
                if cond_G17(n, m):
                    s += 'G17 '
                if cond_G18(n, m):
                    s += 'G18 '
                if cond_G19(n, m):
                    s += 'G19 '
                if cond_G20(n, m):
                    s += 'G20 '
                if cond_G21a(n, m):
                    s += 'G21a '
                if cond_G21b(n, m):
                    s += 'G21b '
                if cond_G21c(n, m):
                    s += 'G21c '
                if cond_G21d(n, m):
                    s += 'G21d '

                if verbose:
                    print(s)
                s = s.strip()
                if s not in fam:
                    fam[s] = [(n, m)]
                else:
                    fam[s].append((n, m))
        if verbose:           
            print()
    return fam


if __name__ == '__main__':

    
    verbose = False
    fam = get_families(5, 50)

    print('Families:')
    for k in sorted(fam):
        displayFam(fam, k, verbose)
    print('Number of families:', len(fam))

