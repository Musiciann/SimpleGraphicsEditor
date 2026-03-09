import math

def identity():
    return [[1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]]

def translation(dx, dy, dz):
    return [[1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [dx, dy, dz, 1.0]]

def scaling(sx, sy, sz):
    return [[sx, 0.0, 0.0, 0.0],
            [0.0, sy, 0.0, 0.0],
            [0.0, 0.0, sz, 0.0],
            [0.0, 0.0, 0.0, 1.0]]

def rotation_x(angle_deg):
    rad = math.radians(angle_deg)
    c = math.cos(rad)
    s = math.sin(rad)
    return [[1.0, 0.0, 0.0, 0.0],
            [0.0, c, s, 0.0],
            [0.0, -s, c, 0.0],
            [0.0, 0.0, 0.0, 1.0]]

def rotation_y(angle_deg):
    rad = math.radians(angle_deg)
    c = math.cos(rad)
    s = math.sin(rad)
    return [[c, 0.0, -s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [s, 0.0, c, 0.0],
            [0.0, 0.0, 0.0, 1.0]]

def rotation_z(angle_deg):
    rad = math.radians(angle_deg)
    c = math.cos(rad)
    s = math.sin(rad)
    return [[c, s, 0.0, 0.0],
            [-s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]]

def reflection(plane):
    if plane == 'xy':
        return [[1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]]
    elif plane == 'xz':
        return [[1.0, 0.0, 0.0, 0.0],
                [0.0, -1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]]
    elif plane == 'yz':
        return [[-1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]]
    else:
        return identity()

def perspective(d):
    return [[1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 1.0/d],
            [0.0, 0.0, 0.0, 1.0]]

def multiply_matrix_vector(mat, vec):
    result = [0.0, 0.0, 0.0, 0.0]
    for j in range(4):
        s = 0.0
        for i in range(4):
            s += vec[i] * mat[i][j]
        result[j] = s
    return result

def apply_transform(vertices, matrix):
    new_verts = []
    for v in vertices:
        v4 = [v[0], v[1], v[2], 1.0]
        v4t = multiply_matrix_vector(matrix, v4)
        if v4t[3] != 0.0:
            new_verts.append([v4t[0]/v4t[3], v4t[1]/v4t[3], v4t[2]/v4t[3]])
        else:
            new_verts.append([v4t[0], v4t[1], v4t[2]])
    return new_verts