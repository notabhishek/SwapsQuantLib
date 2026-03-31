# x = solve(A, b), solves A.x = b while preserving automatic differentiation for Dual numbers

import numpy as np

def pivot_matrix(A):
    """Returns the pivoting matrix for P, used in Doolittle's method."""
    n = A.shape[0]
    P = np.eye(n, dtype="object")
    # Pivot P such that the largest element of each column of A is on diagonal
    for j in range(n):
        # row = np.argmax(np.abs(A[j:, j]))
        row = max(range(j, n), key=lambda i: abs(A[i][j]))
        if j != row:
            P[[j, row]] = P[[row, j]]  # Swap the rows
    return P


def plu_decomp(A):
    """Performs an LU Decomposition of A (which must be square)
    into PA = LU. The function returns P, L and U."""
    n = A.shape[0]
    # Create zero matrices for L and U
    L, U = np.zeros(shape=(n, n)), np.zeros(shape=(n, n))

    # Create the pivot matrix P and the multipled matrix PA
    P = pivot_matrix(A)
    PA = np.matmul(P, A)

    # Perform the LU Decomposition
    for j in range(n):
        # All diagonal entries of L are set to unity
        L[j, j] = 1.0

        # LaTeX: u_{ij} = a_{ij} - \sum_{k=1}^{i-1} u_{kj} l_{ik}
        for i in range(j+1):
            sx = np.matmul(L[i, :i], U[:i, j])
            s1 = sum(U[k][j] * L[i][k] for k in range(i))
            U[i, j] = PA[i, j] - sx

        # LaTeX: l_{ij} = \frac{1}{u_{jj}} (a_{ij} - \sum_{k=1}^{j-1} u_{kj} l_{ik} )
        for i in range(j, n):
            sy = np.matmul(L[i, :j], U[:j, j])
            s2 = sum(U[k][j] * L[i][k] for k in range(j))
            L[i, j] = (PA[i, j] - sy) / U[j, j]

    return P, L, U


def solve_lower_triangular(L, b):
    """solve the equation Lx = b, for L lower diagonal matrix"""
    n, x = L.shape[0], np.zeros_like(b)
    for i in range(n):
        val = b[i, 0] - np.sum(np.matmul(L[i, :i], x[:i, 0]))
        x[i, 0] = val / L[i, i]
    return x


def solve_upper_triangular(U, b):
    """solve the equation Ux = b, for U upper diagonal matrix"""
    return solve_lower_triangular(U[::-1, ::-1], b[::-1, ::-1])[::-1, ::-1]


def solve(A, b):
    """solve the linear system Ax=b, via PAx=LUx=Pb via Ly=Pb and Ux=y"""
    P, L, U = plu_decomp(A)
    y = solve_lower_triangular(L, np.matmul(P, b))
    x = solve_upper_triangular(U, y)
    return x