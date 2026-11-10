# MultiCalculator

Calculadora científica y de matrices (2x2 y 3x3) con backend en **Flask** e historial en **SQLite**.

## Características

- Calculadora con `+ − × ÷`, potencia (`xʸ`), raíz (`√`), porcentaje, paréntesis, cambio de signo y borrado; funciona también con el teclado.
- Matrices 2x2 y 3x3: suma, resta, multiplicación, determinante, inversa y transpuesta.
- Historial persistente en SQLite (se puede borrar desde la interfaz).
- Tema claro/oscuro automático, diseño responsivo y accesible.
- Las expresiones se evalúan en el servidor **sin `eval()`**: se analizan con `ast` y solo se permiten números, operadores aritméticos y `sqrt`.

## Estructura

```
multicalculator/
├── app.py                 # Flask: rutas, API JSON, errores, cabeceras de seguridad
├── database.py            # SQLite (consultas parametrizadas)
├── calculator/
│   ├── engine.py          # evaluador seguro de expresiones
│   └── matrices.py        # operaciones con matrices
├── templates/index.html
├── static/                # style.css, script.js, favicon.svg
└── tests/                 # pruebas del motor, matrices y API
```

## Cómo ejecutarlo

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                    # abre http://127.0.0.1:5000
```

Variables opcionales: `PORT` (por defecto 5000), `FLASK_DEBUG=1` y `MULTICALC_DB` (ruta del archivo SQLite; por defecto `instance/history.db`, que se crea solo).

## API

| Método | Ruta | Cuerpo | Respuesta |
|--------|------|--------|-----------|
| POST | `/api/calculate` | `{"expression": "2*(3+4)"}` | `{"result": "14"}` |
| POST | `/api/matrix` | `{"operation": "mul", "a": [[1,2],[3,4]], "b": [[0,1],[1,0]]}` | `{"result": [[2,1],[4,3]]}` |
| GET | `/api/history` | — | `{"history": [...]}` |
| DELETE | `/api/history` | — | `{"ok": true}` |

Operaciones de matriz: `sum`, `sub`, `mul` (usan A y B) y `det`, `inv`, `trans` (solo A).
Los errores devuelven HTTP 400 con `{"error": "mensaje"}`.

Ejemplo:

```bash
curl -X POST http://127.0.0.1:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "sqrt(16)+2**3"}'
```

## Pruebas

```bash
python -m unittest discover -s tests -t .
# o, si tienes pytest instalado:
pytest
```

## Base de datos

Una sola tabla `history` (`id`, `kind`, `input`, `result`, `created_at`). Se conservan las últimas 500 operaciones. Para inspeccionarla:

```bash
sqlite3 instance/history.db "SELECT * FROM history ORDER BY id DESC LIMIT 10;"
```
