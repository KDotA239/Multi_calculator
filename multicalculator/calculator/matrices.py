"""Operaciones con matrices cuadradas 2x2 y 3x3."""
import math

SUPPORTED_SIZES = (2, 3)

LABELS = {
    "sum": "A + B",
    "sub": "A − B",
    "mul": "A × B",
    "det": "det(A)",
    "inv": "A⁻¹",
    "trans": "Aᵀ",
}


class MatrixError(ValueError):
    """Error causado por los datos del usuario (se responde con HTTP 400)."""


def validate(m, name):
    if not isinstance(m, list) or len(m) not in SUPPORTED_SIZES:
        raise MatrixError(f"La matriz {name} debe ser 2x2 o 3x3")
    n = len(m)
    for row in m:
        if not isinstance(row, list) or len(row) != n:
            raise MatrixError(f"La matriz {name} debe ser cuadrada")
        for v in row:
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise MatrixError(f"La matriz {name} solo admite números finitos")
    return [[float(v) for v in row] for row in m]


def add(a, b):
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def subtract(a, b):
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def multiply(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def transpose(m):
    return [list(col) for col in zip(*m)]


def _minor(m, i, j):
    return [row[:j] + row[j + 1:] for k, row in enumerate(m) if k != i]


def determinant(m):
    n = len(m)
    if n == 1:
        return m[0][0]
    return sum((-1) ** j * m[0][j] * determinant(_minor(m, 0, j)) for j in range(n))


def inverse(m):
    det = determinant(m)
    if abs(det) < 1e-12:
        raise MatrixError("La matriz no es invertible (determinante 0)")
    n = len(m)
    cofactors = [[(-1) ** (i + j) * determinant(_minor(m, i, j)) for j in range(n)] for i in range(n)]
    return [[x / det for x in row] for row in transpose(cofactors)]


def _clean(x):
    r = round(x, 10) + 0.0  # evita -0.0 y ruido de coma flotante
    return int(r) if r.is_integer() else r


_BINARY = {"sum": add, "sub": subtract, "mul": multiply}
_UNARY = {
    "det": lambda m: [[determinant(m)]],
    "inv": inverse,
    "trans": transpose,
}


def compute(operation, a, b=None):
    """Devuelve siempre una lista de filas (el determinante es [[valor]])."""
    if operation in _UNARY:
        result = _UNARY[operation](validate(a, "A"))
    elif operation in _BINARY:
        a, b = validate(a, "A"), validate(b, "B")
        if len(a) != len(b):
            raise MatrixError("Las matrices deben tener el mismo tamaño")
        result = _BINARY[operation](a, b)
    else:
        raise MatrixError("Operación no soportada")
    return [[_clean(x) for x in row] for row in result]
