from typing import Tuple


def sum_tuple(t1: tuple, t2: tuple) -> tuple:
    return tuple([t1[i] + t2[i] for i in range(len(t1))])


def mult_tuple_num(t: tuple, n: float) -> tuple:
    return tuple([i * n for i in t])


def open_list(ls: list) -> list:
    r = []
    for i in ls:
        r += i
    return r


def line_intersection(line1: Tuple[Tuple[float, float], Tuple[float, float]],
                      line2: Tuple[Tuple[float, float], Tuple[float, float]]) -> Tuple[Tuple[float, float], bool]:
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    f = True
    if div == 0:
        div = 10**-6
        f = False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return (x, y), f
