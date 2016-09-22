__author__ = 'Tony39'
"""This is the implementation of the final routines destined to finding the graph"""

import numpy as np


def figure_relevant(l_p1, l_p2, fig_extremes):
    low_x = min(l_p1[0], l_p2[0])
    low_y = min(l_p1[1], l_p2[1])
    hig_x = max(l_p1[0], l_p2[0])
    hig_y = max(l_p1[1], l_p2[1])

    if (low_x > fig_extremes[2]) or (hig_x < fig_extremes[0]) or (low_y > fig_extremes[3]) or (hig_y < fig_extremes[1]):
        return False
    return True


def intersect(l1, l2, points):
    """Returns true if line L1 and L2 intersect
    :rtype : bool
    """
    a1 = points[l1[0]]
    b1 = points[l1[1]]
    a2 = points[l2[0]]
    b2 = points[l2[1]]
    if (a1 == a2) or (a1 == b2) or (b1 == a2) or (b1 == b2):
        return False
    return ccw(a1, b1, a2) != ccw(a1, b1, b2) and ccw(a2, b2, a1) != ccw(a2, b2, b1)


def ccw(a, b, c):
    """Test whether the turn formed by a,b,c is ccw"""
    return (b[0] - a[0]) * (c[1] - a[1]) > (b[1] - a[1]) * (c[0] - a[0])


def intersect_fig(lo, points, lines, fig_idx, start_extremes):
    """Test whether the line lo intersects figure fig_idx"""
    if not (figure_relevant(points[lo[0]], points[lo[1]], start_extremes[fig_idx][2])):
        return False
    ini = start_extremes[fig_idx][0]
    if fig_idx != len(start_extremes) - 1:
        fin = start_extremes[fig_idx + 1][0]
    else:
        fin = len(lines)
    for i in range(ini, fin):
        if intersect(lo, lines[i], points):
            return True
    return False


def find_graph(points, lines, start_extremes):
    n_points = len(points)
    vis_graph = np.array(range(n_points * n_points), bool).reshape((n_points, n_points))
    vis_graph.fill(True)
    cur_fig = 0
    if len(start_extremes) > 1:
        up_bound = start_extremes[1][1]
    else:
        up_bound = len(points)
    for a in range(0, n_points):
        if a >= up_bound:
            cur_fig += 1
            if cur_fig >= len(start_extremes) - 1:
                up_bound = len(points)
            else:
                up_bound = start_extremes[cur_fig][1]

        for b in range(a + 1, n_points):
            lo = [a, b]
            if b > a + 1 and b < up_bound:
                vis_graph[a, b] = False
                vis_graph[b, a] = False
                continue
            for f in range(len(start_extremes)):
                if intersect_fig(lo, points, lines, f, start_extremes):
                    vis_graph[a, b] = False
                    vis_graph[b, a] = False
                    break
    return vis_graph
