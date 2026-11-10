"""Evaluador seguro de expresiones aritméticas.

Nunca usa eval(): la expresión se convierte en un árbol sintáctico (ast) y solo se
recorren los nodos permitidos (números, + - * / **, signo y sqrt). Cualquier otra
cosa (nombres, atributos, llamadas, etc.) se rechaza.
"""
import ast
import math
import operator
import re

MAX_LENGTH = 200
MAX_EXPONENT = 1000


class CalcError(ValueError):
    """Error causado por la expresión del usuario (se responde con HTTP 400)."""


_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}

# "50%" -> "(50/100)". El % solo se admite justo después de un número.
_PERCENT = re.compile(r"(\d+(?:\.\d*)?|\.\d+)%")


def _preprocess(expr: str) -> str:
    expr = expr.replace("^", "**")
    expr = _PERCENT.sub(r"(\1/100)", expr)
    if "%" in expr:
        raise CalcError("El % solo se puede usar justo después de un número")
    return expr


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)

    if isinstance(node, ast.Constant):
        # type() excluye bool; todo se maneja como float para evitar enteros gigantes.
        if type(node.value) in (int, float):
            return float(node.value)
        raise CalcError("Expresión inválida")

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_eval(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise CalcError("El exponente es demasiado grande")
        try:
            result = _BINARY[type(node.op)](left, right)
        except ZeroDivisionError:
            raise CalcError("No se puede dividir entre cero") from None
        except OverflowError:
            raise CalcError("El resultado es demasiado grande") from None
        if isinstance(result, complex):
            raise CalcError("El resultado no es un número real")
        return result

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "sqrt"
        and len(node.args) == 1
        and not node.keywords
    ):
        value = _eval(node.args[0])
        if value < 0:
            raise CalcError("No existe la raíz de un número negativo")
        return math.sqrt(value)

    raise CalcError("Expresión inválida")


def format_number(value: float) -> str:
    """Formato legible: sin '.0' en enteros y sin ruido de coma flotante."""
    value = value + 0.0  # convierte -0.0 en 0.0
    if value == 0:
        return "0"
    if value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.12g}"


def evaluate(expression) -> str:
    if not isinstance(expression, str):
        raise CalcError("La expresión debe ser texto")
    expr = expression.strip()
    if not expr:
        raise CalcError("La expresión está vacía")
    if len(expr) > MAX_LENGTH:
        raise CalcError(f"La expresión es demasiado larga (máximo {MAX_LENGTH} caracteres)")

    expr = _preprocess(expr)
    try:
        tree = ast.parse(expr, mode="eval")
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        raise CalcError("Expresión inválida") from None

    try:
        value = _eval(tree)
    except RecursionError:
        raise CalcError("La expresión es demasiado compleja") from None

    if not math.isfinite(value):
        raise CalcError("El resultado es demasiado grande")
    return format_number(value)
