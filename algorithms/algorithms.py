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