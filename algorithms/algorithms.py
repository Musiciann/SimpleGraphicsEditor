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