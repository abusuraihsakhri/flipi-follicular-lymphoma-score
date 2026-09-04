# Flipi Follicular Lymphoma Score

> **Domain:** Medical Oncology & Cancer Staging Systems
> **Reference Guidelines & Standards:** AJCC Cancer Staging Manual & NCCN Clinical Practice Guidelines

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
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

License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_flipi()`**: Calculate FLIPI score for follicular lymphoma.

  Parameters:
    - age: Patient age in years
    - stage: Ann Arbor stage (1-4)
    - hemoglobin: Hemoglobin level in g/dL
    - ldh_ratio: LDH / upper limit of normal (e.g., 1.5 means 1.5x ULN)
    - nodal_sites: Number of involved nodal sites

  Returns:
    Dict with FLIPI score, risk group, survival estimates, and details.

- **`process_batch()`**: Process a CSV of patients and write FLIPI results.
- **`main()`** — CLI entry point for all commands.

---

## 📐 Mathematical Formulation

```
FLIPI Score = Σ (risk_factors)

risk_factors:
  - age > 60                    → 1 point
  - Ann Arbor stage III or IV   → 1 point
  - Hemoglobin < 12 g/dL        → 1 point
  - LDH > upper limit normal    → 1 point
  - Nodal sites > 4             → 1 point

Risk Groups:
  score 0-1  → Low risk
  score 2    → Intermediate risk
  score ≥3   → High risk
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Patient Evaluation
```bash
python cli.py single --age 65 --stage 4 --hemoglobin 10.0 --ldh-ratio 2.0 --nodal-sites 6
```

### 2. Batch Processing (CSV)
```bash
python cli.py batch --input patients.csv --output results.csv
```

### 3. Enterprise Audit Dispatch
```bash
python cli.py audit --task-id TASK-001
```

### 4. Supervisory Chat (Air-Gapped)
```bash
python cli.py chat "Explain FLIPI scoring"
```

### 5. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### Parameter Reference
- `single`: Evaluate a single patient (requires --age, --stage, --hemoglobin, --ldh-ratio, --nodal-sites)
- `batch`: Batch process CSV file (requires --input, optional --output)
- `audit`: Dispatch audit task (requires --task-id)
- `chat`: Supervisory chat (requires query text)
- `verify-audit`: Verify HMAC audit trail integrity

### Batch CSV Input Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `age` | Patient age in years | Required |
| `stage` | Ann Arbor stage (1-4) | Required |
| `hemoglobin` | Hemoglobin in g/dL | Required |
| `ldh_ratio` | LDH / upper limit of normal | Required |
| `nodal_sites` | Number of involved nodal sites | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation.
* **FastAPI REST API:** Exposes OpenAPI 3.1 REST endpoints and Prometheus metrics (`/metrics`).
* **Multi-Worker Audit System:** InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker.

### Security Notes
- The `AUDIT_SECRET_KEY` environment variable controls HMAC signing. In production, set this to a strong random value.
- Without `AUDIT_SECRET_KEY` set, a random key is generated per process (suitable for development/testing).

---

## 🧪 Testing & Verification

Run the complete test suite:

```bash
pytest -v
```

This runs 31 tests covering:
- FLIPI risk factor scoring
- Risk group classification
- Full calculation scenarios
- Input validation
- Batch processing
- PHI guard enforcement
- Worker agent evaluation
- Supervisor consensus and audit
- Enrichment modules

---

## 🐳 Container Deployment

```bash
docker build -t flipi-follicular-lymphoma-score .
docker run flipi-follicular-lymphoma-score single --age 45 --stage 1 --hemoglobin 14.0 --ldh-ratio 0.9 --nodal-sites 2
```

With docker-compose:
```bash
# Set a strong secret in production
export AUDIT_SECRET_KEY=$(python -c "import os; print(os.urandom(32).hex())")
docker-compose up
```
