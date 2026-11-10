import unittest

from calculator import engine
from calculator.engine import CalcError


class EngineTests(unittest.TestCase):
    def test_aritmetica_basica(self):
        self.assertEqual(engine.evaluate("2+3*4"), "14")
        self.assertEqual(engine.evaluate("(2+3)*4"), "20")
        self.assertEqual(engine.evaluate("2**10"), "1024")
        self.assertEqual(engine.evaluate("2^3"), "8")
        self.assertEqual(engine.evaluate("-(5)+2"), "-3")

    def test_flotantes_sin_ruido(self):
        self.assertEqual(engine.evaluate("0.1+0.2"), "0.3")
        self.assertEqual(engine.evaluate("1/4"), "0.25")

    def test_raiz_y_porcentaje(self):
        self.assertEqual(engine.evaluate("sqrt(16)"), "4")
        self.assertEqual(engine.evaluate("50%"), "0.5")
        self.assertEqual(engine.evaluate("200*10%"), "20")

    def test_errores_de_usuario(self):
        for expr in ["1/0", "sqrt(-1)", "(-8)**0.5", "2+", "", "   ", "5%%", "(%)"]:
            with self.subTest(expr=expr):
                with self.assertRaises(CalcError):
                    engine.evaluate(expr)

    def test_rechaza_codigo_peligroso(self):
        peligrosas = [
            "__import__('os').system('echo hola')",
            "open('/etc/passwd')",
            "().__class__",
            "[1,2,3]",
            "'a'*5",
            "True+1",
            "abs(-1)",
            "x+1",
            "lambda: 1",
        ]
        for expr in peligrosas:
            with self.subTest(expr=expr):
                with self.assertRaises(CalcError):
                    engine.evaluate(expr)

    def test_limites_contra_abuso(self):
        with self.assertRaises(CalcError):
            engine.evaluate("9**9**9**9")
        with self.assertRaises(CalcError):
            engine.evaluate("1+" * 150 + "1")  # supera la longitud máxima
        with self.assertRaises(CalcError):
            engine.evaluate("(" * 150 + "1" + ")" * 150)

    def test_tipo_invalido(self):
        with self.assertRaises(CalcError):
            engine.evaluate(123)
        with self.assertRaises(CalcError):
            engine.evaluate(None)


if __name__ == "__main__":
    unittest.main()
