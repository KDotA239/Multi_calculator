import unittest

from calculator import matrices
from calculator.matrices import MatrixError

A = [[1, 2], [3, 4]]
B = [[0, 1], [1, 0]]
M3 = [[2, 0, 1], [1, 3, 2], [1, 1, 1]]


class MatrixTests(unittest.TestCase):
    def test_suma_resta_multiplicacion(self):
        self.assertEqual(matrices.compute("sum", A, B), [[1, 3], [4, 4]])
        self.assertEqual(matrices.compute("sub", A, B), [[1, 1], [2, 4]])
        self.assertEqual(matrices.compute("mul", A, B), [[2, 1], [4, 3]])

    def test_determinante(self):
        self.assertEqual(matrices.compute("det", A), [[-2]])
        self.assertEqual(matrices.compute("det", M3), [[0 + 2 * (3 - 2) - 0 + 1 * (1 - 3)]])

    def test_transpuesta(self):
        self.assertEqual(matrices.compute("trans", A), [[1, 3], [2, 4]])

    def test_inversa(self):
        self.assertEqual(matrices.compute("inv", [[4, 7], [2, 6]]), [[0.6, -0.7], [-0.2, 0.4]])
        inv = matrices.compute("inv", [[2, 0, 0], [0, 4, 0], [0, 0, 5]])
        self.assertEqual(inv, [[0.5, 0, 0], [0, 0.25, 0], [0, 0, 0.2]])

    def test_inversa_singular(self):
        with self.assertRaises(MatrixError):
            matrices.compute("inv", [[1, 2], [2, 4]])

    def test_validaciones(self):
        invalidos = [
            ("sum", A, None),
            ("sum", A, [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
            ("sum", [[1, 2], [3, "x"]], B),
            ("sum", [[1, 2], [3, True]], B),
            ("sum", [[1, 2], [3]], B),
            ("det", [[1]], None),
            ("potencia", A, B),
        ]
        for op, a, b in invalidos:
            with self.subTest(op=op, a=a, b=b):
                with self.assertRaises(MatrixError):
                    matrices.compute(op, a, b)

    def test_sin_menos_cero(self):
        result = matrices.compute("mul", [[0, 0], [0, 0]], [[-1, -1], [-1, -1]])
        self.assertEqual(str(result), "[[0, 0], [0, 0]]")


if __name__ == "__main__":
    unittest.main()
