# Flipi Follicular Lymphoma Score

> **Domain:** Medical Oncology & Cancer Staging Systems  
> **Reference Guidelines & Standards:** `AJCC Cancer Staging Manual & NCCN Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

FLIPI (Follicular Lymphoma International Prognostic Index)

Calculates the FLIPI score (0-5) and risk group for follicular lymphoma prognosis.

Risk factors (1 point each):
  - Age > 60
  - Ann Arbor Stage III or IV
  - Hemoglobin < 12 g/dL
  - LDH > upper limit of normal
  - Nodal sites > 4

Risk groups:
  Low risk:          0-1 points  → 10-year OS ~71%
  Intermediate risk: 2 points   → 10-year OS ~51%
  High risk:         ≥3 points  → 10-year OS ~36%

Reference: Solal-Céligny et al., Blood 2004;104:1258-1265

Zero-dependency Python implementation.
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_flipi()`**: Calculate FLIPI score for follicular lymphoma.

Parameters:
    age: Patient age in years
    stage: Ann Arbor stage (1-4)
    hemoglobin: Hemoglobin level in g/dL
    ldh_ratio: LDH / upper limit of normal (e.g., 1.5 means 1.5x ULN)
    nodal_sites: Number of involved nodal sites

Returns:
    Dict with FLIPI score, risk group, survival estimates, and details.
- **`process_batch()`**: Process a CSV of patients and write FLIPI results.
- **`main()`** — calculates and validates main parameters.

---

## 📐 Mathematical Formulation & Logic

```text
  Calculate FLIPI score for follicular lymphoma.
  score = 0
  elif score == 2:
  return (
  res = calculate_flipi(
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --input data.csv
```

### Parameter Reference
- `--interactive`: Launch guided terminal interactive wizard.
- `--input <path>`: Evaluate input from JSON or CSV specification.
- `--json`: Output deterministic structured results in JSON format.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t flipi-follicular-lymphoma-score .
docker run -p 8000:8000 flipi-follicular-lymphoma-score
```
