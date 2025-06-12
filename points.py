def get_RV01(n: int, m: int) -> tuple[int, int, int]:
    return (0, 0, 0)


def get_RV02(n, m):
    return (2, 0, 0)


def get_RV03(n, m):
    return (0, 0, 1)


def get_RV04(n, m):
    return (0, (-5 * m + 6 * n - n % 3) / 3, 0)


def get_RV05(n, m):
    return (1, -m + 3 * n / 2 - 3 / 2, 2 * m - 3 * n / 2 - 1 / 2)


def get_RV06(n, m):
    return (0, 0, 5 * m - 6 * n)


##########


def get_MV07(n, m, a, b, c):
    return (
        (6 * n - 5 * m + (b - 3 * a) * ((m - 2 * n) % 4) - (c * (-5 * m + 6 * n)) % 4)
        / 4,
        a * ((m - 2 * n) % 4),
        b * ((m - 2 * n) % 4),
    )


def get_RV07a(n, m):
    return get_MV07(n, m, 1, 0, 0)


def get_RV07b(n, m):
    return get_MV07(n, m, 0, 1, 0)


def get_RV07c(n, m):
    return get_MV07(n, m, 0, 0, 1)


##########


def get_MV08(n, m, a, b, c, d):
    return (
        a + 2 * b + d,
        (3 * n - 2 * m - (4 * a + 6 * b + 3 * d) + (d - 1) * (n % 2)) / 2,
        (4 * m - 3 * n - (2 * a + 2 * b + d) + (d - 2 * c - 1) * (n % 2)) / 2,
    )


def get_RV08a(n, m):
    return get_MV08(n, m, 1, 0, 0, 0)


def get_RV08b(n, m):
    return get_MV08(n, m, 0, 1, 0, 0)


def get_RV08c(n, m):
    return get_MV08(n, m, 0, 0, 1, 0)


def get_RV08d(n, m):
    return get_MV08(n, m, 0, 0, 0, 1)


"""
def get_RV15(n, m):
    return (1, (3*n-2*m-4-(n%2))/2, (4*m-3*n-2-(n%2))/2)

def get_RV16(n, m):
    return (2, (3*n-2*m-6-(n%2))/2, (4*m-3*n-2-(n%2))/2)

def get_RV03(n, m):
    return (0, (3*n-2*m-0-(n%2))/2, (4*m-3*n-3*(n%2))/2)
"""

##########


def get_MV09(n, m, a, b, c):
    return (
        (a + b) * (3 * m - 3 * n - 1 - a),
        (a + c) * (3 * m - 3 * n - 2),
        6 * m - 6 * n - 1 - 2 * c,
    )


def get_RV09a(n, m):
    return get_MV09(n, m, 1, 0, 0)


def get_RV09b(n, m):
    return get_MV09(n, m, 0, 1, 0)


def get_RV09c(n, m):
    return get_MV09(n, m, 0, 0, 1)


"""

def get_RV13(n, m):
    return (3*m - 3*n - 2, 3*m - 3*n - 2, 6*m - 6*n - 1)

def get_RV14(n, m):
    return (3*m - 3*n - 1, 0, 6*m - 6*n - 1)

def get_RV11(n, m):
    return (0, 3*m - 3*n - 2, 6*m - 6*n - 3)

"""

##########


def get_MV10(n, m, a, b, c):
    return (
        b * (m % 3),
        (-5 * m + 6 * n - ((a + 4 * b) * (m % 3)) + c * ((-m) % 3)) / 3,
        c * ((-m) % 3),
    )


def get_RV10a(n, m):
    return get_MV10(n, m, 1, 0, 0)


def get_RV10b(n, m):
    return get_MV10(n, m, 0, 1, 0)


def get_RV10c(n, m):
    return get_MV10(n, m, 0, 0, 1)


"""
def get_RV07(n, m):
    return (0, (-5*m + 6*n - (m%3))/3, 0)

def get_RV19b(n, m):
    return (m%3, (-5*m + 6*n - 4*(m%3))/3, 0)

def get_RV20(n, m):
    return (0, (-5*m + 6*n + ((-m)%3))/3, (-m)%3)
"""

##########


def get_MV11(n, m, a, b, c):
    return (
        -2 * m / 3 + n - (a + c) * (m % 3) / 3 - ((2 * b) * ((2*m) % 3)) / 3,
        b * ((2*m) % 3),
        7 * m / 3 - 2 * n - ((4 * a + c) * (m % 3)) / 3 + (b * ((2*m) % 3)) / 3,
    )


def get_RV11a(n, m):
    return get_MV11(n, m, 1, 0, 0)


def get_RV11b(n, m):
    return get_MV11(n, m, 0, 1, 0)


def get_RV11c(n, m):
    return get_MV11(n, m, 0, 0, 1)


"""
def get_RV22(n, m):
    return (-2*m/3 + n - (m%3)/3, 0, 7*m/3 - 2*n - 4*(m%3)/3)

def get_RV23(n, m):
    return (-2*m/3 + n - 2*((-m)%3)/3, (-m)%3, 7*m/3 - 2*n + (-m)%3/3)

def get_RV18(n, m):
    return (-2*m/3 + n - (m%3)/3, 0, 7*m/3 - 2*n - (m%3)/3)
"""

##########


def get_MV12(n, m, a, b, c):
    return (
        c,
        a * (-3 * m + 3 * n + 1),
        b * (3 * m - 3 * n - 1) + c * (3 * m - 3 * n + 1),
    )


def get_RV12a(n, m):
    return get_MV12(n, m, 1, 0, 0)


def get_RV12b(n, m):
    return get_MV12(n, m, 0, 1, 0)


def get_RV12c(n, m):
    return get_MV12(n, m, 0, 0, 1)


"""
def get_RV31(n, m):
    return (0, -3*m + 3*n + 1, 0)

def get_RV38(n, m):
    return (0, 0, 3*m - 3*n - 1)

def get_RV10(n, m):
    return (1, 0, 3*m - 3*n + 1)
"""

##########


def get_RV_P6_6(n, m):  # created only for (6, 6)
    return (1, 1, 1)


def get_RV_P7_8(n, m):  # created only for (7, 8)
    return (1, 0, 3)


def get_RV_P8_8(n, m):  # created only for (8, 8)
    return (2, 0, 1)


points = [
    "V01",
    "V02",
    "V03",
    # "V04",
    "V06",
    "V07a",
    "V07b",
    "V07c",
    "V08a",
    "V08b",
    "V08c",
    "V08d",
    "V09a",
    "V09b",
    "V09c",
    "V10a",
    "V10b",
    "V10c",
    "V11a",
    "V11b",
    "V11c",
    "V12a",
    "V12b",
    "V12c",
    "V_P6_6",
    "V_P7_8",
    "V_P8_8",
]

NEW_NAMES = {
    "V01": "V01",
    "V02": "V02",
    "V03": "V03",
    "V04": "V06",
    "V05": "V07a",
    "V06": "V07b",
    "V07": "V07c",
    "V08": "V08a",
    "V09": "V08b",
    "V10": "V08c",
    "V11": "V08d",
    "V12": "V09a",
    "V13": "V09b",
    "V14": "V09c",
    "V15": "V10a",
    "V16": "V10b",
    "V17": "V10c",
    "V18": "V11a",
    "V19": "V11b",
    "V20": "V11c",
    "V21": "V12a",
    "V22": "V12b",
    "V23": "V12c",
}
