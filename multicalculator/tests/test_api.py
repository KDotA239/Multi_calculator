import tempfile
import unittest
from pathlib import Path

from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app = create_app({"TESTING": True, "DATABASE": str(Path(self.tmp.name) / "test.db")})
        self.client = app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_pagina_principal(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Content-Security-Policy", res.headers)
        self.assertIn("MultiCalculator", res.get_data(as_text=True))

    def test_calcular_y_guardar_historial(self):
        res = self.client.post("/api/calculate", json={"expression": "2*(3+4)"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["result"], "14")

        history = self.client.get("/api/history").get_json()["history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["kind"], "calculo")
        self.assertEqual(history[0]["input"], "2*(3+4)")
        self.assertEqual(history[0]["result"], "14")

    def test_error_de_calculo_no_se_guarda(self):
        res = self.client.post("/api/calculate", json={"expression": "1/0"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())
        self.assertEqual(self.client.get("/api/history").get_json()["history"], [])

    def test_no_ejecuta_codigo(self):
        res = self.client.post("/api/calculate", json={"expression": "__import__('os').getcwd()"})
        self.assertEqual(res.status_code, 400)

    def test_cuerpo_invalido(self):
        res = self.client.post("/api/calculate", data="no es json", content_type="text/plain")
        self.assertEqual(res.status_code, 400)
        res = self.client.post("/api/calculate", json={"expression": 5})
        self.assertEqual(res.status_code, 400)

    def test_matrices(self):
        res = self.client.post(
            "/api/matrix", json={"operation": "mul", "a": [[1, 2], [3, 4]], "b": [[0, 1], [1, 0]]}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["result"], [[2, 1], [4, 3]])

        res = self.client.post("/api/matrix", json={"operation": "inv", "a": [[1, 2], [2, 4]]})
        self.assertEqual(res.status_code, 400)

        history = self.client.get("/api/history").get_json()["history"]
        self.assertEqual([h["kind"] for h in history], ["matriz"])

    def test_borrar_historial(self):
        self.client.post("/api/calculate", json={"expression": "1+1"})
        self.assertEqual(self.client.delete("/api/history").status_code, 200)
        self.assertEqual(self.client.get("/api/history").get_json()["history"], [])

    def test_errores_http_en_json(self):
        res = self.client.get("/api/no-existe")
        self.assertEqual(res.status_code, 404)
        self.assertIn("error", res.get_json())
        res = self.client.get("/api/calculate")
        self.assertEqual(res.status_code, 405)


if __name__ == "__main__":
    unittest.main()
