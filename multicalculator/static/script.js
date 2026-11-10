"use strict";

const display = document.getElementById("display");
const sizeSelect = document.getElementById("matrix-size");
const matrixResult = document.getElementById("matrix-result");
const historyList = document.getElementById("history-list");

let expression = "";
let justCalculated = false;

/* ---------- Utilidades ---------- */
async function api(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Error del servidor");
  return data;
}

const pretty = (s) =>
  s.replace(/\*\*/g, "^").replace(/\*/g, "×").replace(/\//g, "÷").replace(/sqrt\(/g, "√(");

function render(text, isError = false) {
  display.textContent = text === "" ? "0" : pretty(text);
  display.classList.toggle("error", isError);
}

/* ---------- Calculadora ---------- */
function append(value) {
  // Tras un resultado, un número o paréntesis empieza una cuenta nueva.
  if (justCalculated && /^[\d.(s]/.test(value)) expression = "";
  justCalculated = false;
  expression += value;
  render(expression);
}

function backspace() {
  expression = expression.endsWith("sqrt(")
    ? expression.slice(0, -5)
    : expression.slice(0, -1);
  render(expression);
}

function clearAll() {
  expression = "";
  justCalculated = false;
  render("");
}

function negate() {
  if (!expression) return;
  if (/^-?[\d.]+(e[+-]?\d+)?$/i.test(expression)) {
    expression = expression.startsWith("-") ? expression.slice(1) : "-" + expression;
  } else {
    expression = `-(${expression})`;
  }
  justCalculated = false;
  render(expression);
}

async function calculate() {
  if (!expression) return;
  try {
    const { result } = await api("/api/calculate", {
      method: "POST",
      body: JSON.stringify({ expression }),
    });
    expression = String(result);
    justCalculated = true;
    render(expression);
    loadHistory();
  } catch (err) {
    render(err.message, true);
    expression = "";
  }
}

document.getElementById("keys").addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const { action, value } = btn.dataset;
  if (value) append(value);
  else if (action === "clear") clearAll();
  else if (action === "back") backspace();
  else if (action === "negate") negate();
  else if (action === "equals") calculate();
});

document.addEventListener("keydown", (e) => {
  // Ignora campos de formulario y botones ajenos al teclado numérico.
  if (e.target.closest("input, select, textarea")) return;
  if (e.target.closest("button") && !e.target.closest("#keys")) return;
  if (/^[\d+\-*/().%]$/.test(e.key)) append(e.key);
  else if (e.key === "^") append("**");
  else if (e.key === "Enter" || e.key === "=") { e.preventDefault(); calculate(); }
  else if (e.key === "Backspace") backspace();
  else if (e.key === "Escape") clearAll();
});

/* ---------- Matrices ---------- */
function buildMatrix(containerId, n) {
  const box = document.getElementById(containerId);
  box.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
  box.replaceChildren();
  for (let i = 0; i < n * n; i++) {
    const input = document.createElement("input");
    input.type = "number";
    input.step = "any";
    input.value = "0";
    input.setAttribute(
      "aria-label",
      `${containerId} fila ${Math.floor(i / n) + 1} columna ${(i % n) + 1}`
    );
    box.appendChild(input);
  }
}

function readMatrix(containerId, n) {
  const values = [...document.querySelectorAll(`#${containerId} input`)].map((i) => Number(i.value));
  return Array.from({ length: n }, (_, r) => values.slice(r * n, r * n + n));
}

function renderMatrixResult(rows) {
  const table = document.createElement("table");
  table.className = "result-table";
  for (const row of rows) {
    const tr = table.insertRow();
    for (const value of row) tr.insertCell().textContent = value;
  }
  matrixResult.replaceChildren(table);
}

function buildBoth() {
  const n = Number(sizeSelect.value);
  buildMatrix("matrixA", n);
  buildMatrix("matrixB", n);
  matrixResult.textContent = "Aún no hay resultado.";
  matrixResult.classList.remove("error");
}

sizeSelect.addEventListener("change", buildBoth);

document.querySelectorAll("[data-matrix-op]").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const n = Number(sizeSelect.value);
    try {
      const { result } = await api("/api/matrix", {
        method: "POST",
        body: JSON.stringify({
          operation: btn.dataset.matrixOp,
          a: readMatrix("matrixA", n),
          b: readMatrix("matrixB", n),
        }),
      });
      matrixResult.classList.remove("error");
      renderMatrixResult(result);
      loadHistory();
    } catch (err) {
      matrixResult.classList.add("error");
      matrixResult.textContent = err.message;
    }
  });
});

/* ---------- Historial ---------- */
async function loadHistory() {
  try {
    const { history } = await api("/api/history");
    historyList.replaceChildren();
    if (!history.length) {
      const li = document.createElement("li");
      li.className = "empty";
      li.textContent = "Todavía no hay operaciones guardadas.";
      historyList.appendChild(li);
      return;
    }
    for (const item of history) {
      const li = document.createElement("li");
      const text = document.createElement("code");
      text.textContent =
        item.kind === "calculo"
          ? `${pretty(item.input)} = ${item.result}`
          : `${item.input} → ${item.result}`;
      const meta = document.createElement("span");
      meta.className = "meta";
      meta.textContent = item.created_at;
      li.append(text, meta);
      historyList.appendChild(li);
    }
  } catch (err) {
    console.error(err);
  }
}

document.getElementById("clear-history").addEventListener("click", async () => {
  await api("/api/history", { method: "DELETE" });
  loadHistory();
});

/* ---------- Inicio ---------- */
buildBoth();
loadHistory();
