def point_in_poly(point, poly):

    x = point[0]
    y = point[1]

    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def get_rectangle(sw, ne):
    nw = (sw[0], ne[1])
    se = (ne[0], sw[1])
    print sw, se, ne, nw
    return [sw, se, ne, nw]

area = get_rectangle((-23.612474, -46.702746), (-23.589548, -46.673392))
point = (-23.592466, -46.683393)

print point_in_poly(point, area)
