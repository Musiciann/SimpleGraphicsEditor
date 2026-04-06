import math

def dda_algorithm_pixels(x1, y1, x2, y2):
    pixels = []
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(int(x1), int(y1))]
    x_inc = dx / steps
    y_inc = dy / steps
    x = x1
    y = y1
    for i in range(steps + 1):
        pixels.append((int(round(x)), int(round(y))))
        x += x_inc
        y += y_inc
    return pixels

def bresenham_algorithm_pixels(x1, y1, x2, y2):
    pixels = []
    x1, y1 = int(x1), int(y1)
    x2, y2 = int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        pixels.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return pixels

def wu_algorithm_pixels(x1, y1, x2, y2):
    pixels = []
    steep = abs(y2 - y1) > abs(x2 - x1)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0:
        gradient = 1.0
    else:
        gradient = dy / dx
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = 1 - (x1 + 0.5) % 1
    xpxl1 = xend
    ypxl1 = int(yend)
    if steep:
        pixels.append((ypxl1, xpxl1, (1 - (yend % 1)) * xgap))
        pixels.append((ypxl1 + 1, xpxl1, (yend % 1) * xgap))
    else:
        pixels.append((xpxl1, ypxl1, (1 - (yend % 1)) * xgap))
        pixels.append((xpxl1, ypxl1 + 1, (yend % 1) * xgap))
    intery = yend + gradient
    xend = round(x2)
    yend = y2 + gradient * (xend - x2)
    xgap = (x2 + 0.5) % 1
    xpxl2 = xend
    ypxl2 = int(yend)
    if steep:
        pixels.append((ypxl2, xpxl2, (1 - (yend % 1)) * xgap))
        pixels.append((ypxl2 + 1, xpxl2, (yend % 1) * xgap))
    else:
        pixels.append((xpxl2, ypxl2, (1 - (yend % 1)) * xgap))
        pixels.append((xpxl2, ypxl2 + 1, (yend % 1) * xgap))
    for x in range(int(xpxl1) + 1, int(xpxl2)):
        if steep:
            pixels.append((int(intery), x, 1 - (intery % 1)))
            pixels.append((int(intery) + 1, x, intery % 1))
        else:
            pixels.append((x, int(intery), 1 - (intery % 1)))
            pixels.append((x, int(intery) + 1, intery % 1))
        intery += gradient
    return pixels

def bresenham_circle_pixels(cx, cy, r):
    pixels = []
    x = 0
    y = r
    delta = 2 - 2 * r
    def plot_symmetry(px, py):
        pixels.append((cx + px, cy + py))
        pixels.append((cx - px, cy + py))
        pixels.append((cx + px, cy - py))
        pixels.append((cx - px, cy - py))
        pixels.append((cx + py, cy + px))
        pixels.append((cx - py, cy + px))
        pixels.append((cx + py, cy - px))
        pixels.append((cx - py, cy - px))
    while y >= x:
        plot_symmetry(x, y)
        if delta < 0:
            d = 2 * (delta + y) - 1
            if d <= 0:
                x += 1
                delta += 2 * x + 1
            else:
                x += 1
                y -= 1
                delta += 2 * (x - y + 1)
        elif delta > 0:
            d = 2 * (delta - x) - 1
            if d <= 0:
                x += 1
                y -= 1
                delta += 2 * (x - y + 1)
            else:
                y -= 1
                delta -= 2 * y + 1
        else:
            x += 1
            y -= 1
            delta += 2 * (x - y + 1)
    return pixels

def bresenham_ellipse_pixels(cx, cy, a, b):
    pixels = []
    if a <= 0 or b <= 0:
        return pixels
    x = 0
    y = b
    a_sq = a * a
    b_sq = b * b
    d = b_sq - a_sq * b + a_sq / 4
    while a_sq * (y - 0.5) > b_sq * (x + 1):
        pixels.append((cx + x, cy + y))
        pixels.append((cx - x, cy + y))
        pixels.append((cx + x, cy - y))
        pixels.append((cx - x, cy - y))
        if d < 0:
            d += b_sq * (2 * x + 3)
            x += 1
        else:
            d += b_sq * (2 * x + 3) + a_sq * (2 - 2 * y)
            x += 1
            y -= 1
    d = b_sq * (x + 0.5) * (x + 0.5) + a_sq * (y - 1) * (y - 1) - a_sq * b_sq
    while y >= 0:
        pixels.append((cx + x, cy + y))
        pixels.append((cx - x, cy + y))
        pixels.append((cx + x, cy - y))
        pixels.append((cx - x, cy - y))
        if d < 0:
            d += b_sq * (2 * x + 2) + a_sq * (3 - 2 * y)
            x += 1
            y -= 1
        else:
            d += a_sq * (3 - 2 * y)
            y -= 1
    return pixels

def interpolate_pixels(points):
    if len(points) < 2:
        return points
    result = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        line = bresenham_algorithm_pixels(x1, y1, x2, y2)
        if result and result[-1] == line[0]:
            result.extend(line[1:])
        else:
            result.extend(line)
    return result

def bresenham_parabola_pixels(p):
    if p <= 0:
        return []
    pos_branch = []
    neg_branch = []
    max_x = 2000
    for x in range(max_x + 1):
        y_sq = 2 * p * x
        y = int(round(math.sqrt(y_sq)))
        pos_branch.append((x, y))
        neg_branch.append((x, -y))
    return [pos_branch, neg_branch]

def bresenham_hyperbola_pixels(a, b):
    if a <= 0 or b <= 0:
        return []
    right_up = []
    right_down = []
    left_up = []
    left_down = []
    max_x = a + 2000
    for x in range(a, max_x + 1):
        y = int(round(b * math.sqrt((x / a) ** 2 - 1)))
        right_up.append((x, y))
        right_down.append((x, -y))
    for x in range(-max_x, -a + 1):
        y = int(round(b * math.sqrt((x / a) ** 2 - 1)))
        left_up.append((x, y))
        left_down.append((x, -y))
    return [right_up, right_down, left_up, left_down]

def rotate_pixels(pixels, angle, cx, cy):
    new_pixels = []
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    for x, y in pixels:
        tx = x - cx
        ty = y - cy
        rx = tx * cos_a - ty * sin_a
        ry = tx * sin_a + ty * cos_a
        new_pixels.append((int(round(rx + cx)), int(round(ry + cy))))
    return new_pixels

def circumcircle(ax, ay, bx, by, cx, cy):
    d = 2 * (ax*(by - cy) + bx*(cy - ay) + cx*(ay - by))
    if abs(d) < 1e-9:
        return (0, 0, float('inf'))
    ux = ((ax*ax + ay*ay)*(by - cy) + (bx*bx + by*by)*(cy - ay) + (cx*cx + cy*cy)*(ay - by)) / d
    uy = ((ax*ax + ay*ay)*(cx - bx) + (bx*bx + by*by)*(ax - cx) + (cx*cx + cy*cy)*(bx - ax)) / d
    dx = ax - ux
    dy = ay - uy
    return (ux, uy, dx*dx + dy*dy)

def is_point_in_circumcircle(px, py, ax, ay, bx, by, cx, cy):

    _, _, rad_sq = circumcircle(ax, ay, bx, by, cx, cy)
    dx = px - ax
    dy = py - ay

    cx_, cy_, rad_sq = circumcircle(ax, ay, bx, by, cx, cy)
    return (px - cx_)**2 + (py - cy_)**2 < rad_sq - 1e-9

def delaunay_triangulation(points):

    if len(points) < 3:
        return []

    min_x = min(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)
    dx = max_x - min_x
    dy = max_y - min_y
    margin = max(dx, dy) * 2
    p1 = (min_x - margin, min_y - margin)
    p2 = (min_x + 2*margin, min_y - margin)
    p3 = (min_x + margin, min_y + 2*margin)

    pts = points + [p1, p2, p3]
    super_indices = (len(points), len(points)+1, len(points)+2)
    triangles = [super_indices]
    for i, p in enumerate(points):
        bad_triangles = []
        for tri in triangles:
            a, b, c = tri
            if is_point_in_circumcircle(p[0], p[1], pts[a][0], pts[a][1], pts[b][0], pts[b][1], pts[c][0], pts[c][1]):
                bad_triangles.append(tri)

        edge_count = {}
        for tri in bad_triangles:
            for edge in [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]:
                e = tuple(sorted(edge))
                edge_count[e] = edge_count.get(e, 0) + 1
        boundary = [e for e, cnt in edge_count.items() if cnt == 1]

        triangles = [t for t in triangles if t not in bad_triangles]

        for e in boundary:
            triangles.append((e[0], e[1], i))

    result = []
    for tri in triangles:
        if not any(v in tri for v in super_indices):
            result.append(tri)
    return result

def clip_line_to_rect(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    INSIDE = 0
    LEFT = 1
    RIGHT = 2
    BOTTOM = 4
    TOP = 8
    def compute_code(x, y):
        code = INSIDE
        if x < xmin: code |= LEFT
        elif x > xmax: code |= RIGHT
        if y < ymin: code |= BOTTOM
        elif y > ymax: code |= TOP
        return code
    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)
    while True:
        if (code1 | code2) == 0:
            return (x1, y1, x2, y2)
        if (code1 & code2) != 0:
            return None
        code_out = code1 if code1 != 0 else code2
        x, y = 0, 0
        if code_out & TOP:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax
        elif code_out & BOTTOM:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin
        elif code_out & RIGHT:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax
        elif code_out & LEFT:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin
        if code_out == code1:
            x1, y1 = x, y
            code1 = compute_code(x1, y1)
        else:
            x2, y2 = x, y
            code2 = compute_code(x2, y2)

def voronoi_from_delaunay(points, triangles, width, height):

    circumcenters = []
    for tri in triangles:
        a, b, c = tri
        p1 = points[a]
        p2 = points[b]
        p3 = points[c]
        cx, cy, _ = circumcircle(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
        circumcenters.append((cx, cy))

    edge_to_tri = {}
    for idx, tri in enumerate(triangles):
        edges = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]
        for e in edges:
            key = tuple(sorted(e))
            edge_to_tri.setdefault(key, []).append(idx)

    segments = []

    for edge, tris in edge_to_tri.items():
        if len(tris) == 2:
            i1, i2 = tris
            segments.append((circumcenters[i1], circumcenters[i2]))
        elif len(tris) == 1:

            tri_idx = tris[0]
            tri = triangles[tri_idx]

            edge_verts = set(edge)
            for v in tri:
                if v not in edge_verts:
                    opposite = v
                    break

            pA = points[edge[0]]
            pB = points[edge[1]]
            mid = ((pA[0]+pB[0])/2, (pA[1]+pB[1])/2)
            interior = points[opposite]
            inward = (interior[0]-mid[0], interior[1]-mid[1])

            edge_dir = (pB[0]-pA[0], pB[1]-pA[1])

            normal = (edge_dir[1], -edge_dir[0])
            if normal[0]*inward[0] + normal[1]*inward[1] > 0:
                normal = (-normal[0], -normal[1])

            length = math.hypot(normal[0], normal[1])
            if length > 0:
                normal = (normal[0]/length, normal[1]/length)
            else:
                normal = (1, 0)
            C = circumcenters[tri_idx]
            far = (C[0] + normal[0]*max(width, height)*2, C[1] + normal[1]*max(width, height)*2)
            clipped = clip_line_to_rect(C[0], C[1], far[0], far[1], 0, 0, width, height)
            if clipped:
                segments.append(((clipped[0], clipped[1]), (clipped[2], clipped[3])))
    return segments

def get_circumcircles(triangles, points):
    circles = []
    for tri in triangles:
        a, b, c = tri
        p1 = points[a]
        p2 = points[b]
        p3 = points[c]
        cx, cy, rad_sq = circumcircle(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
        if rad_sq < float('inf'):
            circles.append((cx, cy, math.sqrt(rad_sq)))
    return circles