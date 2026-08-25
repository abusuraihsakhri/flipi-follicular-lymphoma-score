# FLIPI (Follicular Lymphoma International Prognostic Index)

Real implementation of the FLIPI scoring system for follicular lymphoma prognosis.

## What It Does

Calculates the **FLIPI score (0-5)** and **risk group** based on five clinical risk factors:

| Risk Factor | Criterion | Points |
|-------------|-----------|--------|
| Age | >60 years | 1 |
| Ann Arbor Stage | III or IV | 1 |
| Hemoglobin | <12 g/dL | 1 |
| LDH | >upper limit of normal | 1 |
| Nodal sites | >4 | 1 |

**Risk Groups and Survival:**
| Group | Score | 5-Year OS | 10-Year OS |
|-------|-------|-----------|------------|
| Low | 0-1 | ~91% | ~71% |
| Intermediate | 2 | ~78% | ~51% |
| High | ≥3 | ~53% | ~36% |

## Installation

Zero dependencies — Python 3.7+ stdlib only.

## Usage

### Single Patient

```bash
python flipi_score.py single \
  --age 65 --stage 4 --hemoglobin 10.5 \
  --ldh-ratio 1.5 --nodal-sites 6
```

### Batch Processing

```bash
python flipi_score.py batch -i patients.csv -o results.csv
```

CSV columns: `age`, `stage`, `hemoglobin`, `ldh_ratio`, `nodal_sites`

### Python API

```python
from flipi_score import calculate_flipi

result = calculate_flipi(
    age=65, stage=4, hemoglobin=10.5, ldh_ratio=1.5, nodal_sites=6,
)
print(result["flipi_score"])           # 5
print(result["flipi_risk_group"])      # "High"
print(result["ten_year_survival_pct"]) # 36.0
```

## Running Tests

```bash
python -m pytest test_flipi_score.py -v
```

## Clinical Reference

Solal-Céligny P et al. Follicular lymphoma international prognostic index. Blood. 2004;104(5):1258-1265.

## License

MIT
