"""MultiCalculator: aplicación Flask (interfaz web + API JSON + historial en SQLite)."""
import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

import database
from calculator import engine, matrices

BASE_DIR = Path(__file__).resolve().parent


class ApiError(Exception):
    """Petición mal formada (HTTP 400)."""


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.environ.get("MULTICALC_DB", str(BASE_DIR / "instance" / "history.db")),
        MAX_CONTENT_LENGTH=16 * 1024,  # las peticiones son diminutas; 16 KB sobra
    )
    if config:
        app.config.update(config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    database.init_db(app.config["DATABASE"])

    def json_body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ApiError("Se esperaba un cuerpo JSON válido")
        return data

    # ---------- Páginas ----------
    @app.get("/")
    def index():
        return render_template("index.html")

    # ---------- API ----------
    @app.post("/api/calculate")
    def calculate():
        expression = json_body().get("expression")
        result = engine.evaluate(expression)
        database.add_entry(app.config["DATABASE"], "calculo", expression.strip(), result)
        return jsonify(result=result)

    @app.post("/api/matrix")
    def matrix():
        data = json_body()
        operation, a, b = data.get("operation"), data.get("a"), data.get("b")
        result = matrices.compute(operation, a, b)

        label = matrices.LABELS[operation]
        compact = lambda m: json.dumps(m, separators=(",", ":"))
        description = f"{label}  A={compact(a)}"
        if operation in ("sum", "sub", "mul"):
            description += f"  B={compact(b)}"
        result_text = str(result[0][0]) if operation == "det" else compact(result)
        database.add_entry(app.config["DATABASE"], "matriz", description, result_text)
        return jsonify(result=result)

    @app.get("/api/history")
    def history():
        return jsonify(history=database.list_entries(app.config["DATABASE"]))

    @app.delete("/api/history")
    def clear_history():
        database.clear(app.config["DATABASE"])
        return jsonify(ok=True)

    # ---------- Errores ----------
    @app.errorhandler(ApiError)
    @app.errorhandler(engine.CalcError)
    @app.errorhandler(matrices.MatrixError)
    def user_error(err):
        return jsonify(error=str(err)), 400

    @app.errorhandler(HTTPException)
    def http_error(err):
        if request.path.startswith("/api/"):
            return jsonify(error=err.description), err.code
        return err

    @app.errorhandler(Exception)
    def unexpected_error(err):
        app.logger.exception("Error no controlado")
        if request.path.startswith("/api/"):
            return jsonify(error="Error interno del servidor"), 500
        return "Error interno del servidor", 500

    # ---------- Cabeceras de seguridad ----------
    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'"
        )
        return response

    return app


if __name__ == "__main__":
    create_app().run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
