def mat_vec_mult(A, v):
    m = len(A)
    n = len(A[0])
    result = [0] * m
    for i in range(m):
        s = 0
        for j in range(n):
            s += A[i][j] * v[j]
        result[i] = s
    return result

M_H = [
    [ 2, -2,  1,  1],
    [-3,  3, -2, -1],
    [ 0,  0,  1,  0],
    [ 1,  0,  0,  0]
]

M_B = [
    [-1,  3, -3,  1],
    [ 3, -6,  3,  0],
    [-3,  3,  0,  0],
    [ 1,  0,  0,  0]
]

M_BS = [
    [-1,  3, -3,  1],
    [ 3, -6,  3,  0],
    [-3,  0,  3,  0],
    [ 1,  4,  1,  0]
]

def hermite_coeffs(P1, P4, R1, R4):
    Gx = [P1[0], P4[0], R1[0], R4[0]]
    Gy = [P1[1], P4[1], R1[1], R4[1]]
    coeffs_x = mat_vec_mult(M_H, Gx)
    coeffs_y = mat_vec_mult(M_H, Gy)
    return coeffs_x, coeffs_y

def bezier_coeffs(P1, P2, P3, P4):
    Gx = [P1[0], P2[0], P3[0], P4[0]]
    Gy = [P1[1], P2[1], P3[1], P4[1]]
    coeffs_x = mat_vec_mult(M_B, Gx)
    coeffs_y = mat_vec_mult(M_B, Gy)
    return coeffs_x, coeffs_y

def bspline_coeffs(P0, P1, P2, P3):
    Gx = [P0[0], P1[0], P2[0], P3[0]]
    Gy = [P0[1], P1[1], P2[1], P3[1]]
    coeffs_x = mat_vec_mult(M_BS, Gx)
    coeffs_y = mat_vec_mult(M_BS, Gy)

    coeffs_x = [c / 6.0 for c in coeffs_x]
    coeffs_y = [c / 6.0 for c in coeffs_y]
    return coeffs_x, coeffs_y

def eval_poly(coeffs, t):
    return ((coeffs[0] * t + coeffs[1]) * t + coeffs[2]) * t + coeffs[3]