# FLIPI — Follicular Lymphoma International Prognostic Index

### [Open the Live Application →](https://abusuraihsakhri.github.io/flipi-follicular-lymphoma-score/)

A classical **FLIPI-1** prognostic score calculator for follicular lymphoma. It includes a standalone browser interface, a zero-dependency Python calculation/CLI, batch CSV scoring, and an optional FastAPI endpoint.

## Scoring

One point for each of five adverse factors:

| Factor | Scores 1 point when |
| --- | --- |
| Age | > 60 years |
| Ann Arbor stage | III or IV |
| Hemoglobin | < 12 g/dL |
| Serum lactate dehydrogenase (LDH) | Above the laboratory upper limit of normal (ULN) |
| Involved nodal areas | > 4 anatomical areas (not individual nodes) |

| Score | Risk group | Historical 5-year overall survival | Historical 10-year overall survival |
| --- | --- | --- | --- |
| 0–1 | Low | 91% | 71% |
| 2 | Intermediate | 78% | 51% |
| 3–5 | High | 53% | 36% |

**Interpretation:** Survival percentages are rounded values from the original historical cohort, not personalized predictions for current treatment settings. FLIPI is a prognostic index, **not** a rule for initiating or choosing treatment; symptoms, tumor burden and specialist judgment remain essential. FLIPI-2 and other newer models are not implemented here.

Primary reference: Solal-Céligny P et al. *Blood*. 2004;104(5):1258–1265. [doi:10.1182/blood-2003-12-4434](https://doi.org/10.1182/blood-2003-12-4434). See also the [NCI treatment PDQ](https://www.cancer.gov/types/lymphoma/hp/indolent-b-cell-lymphoma-treatment-pdq) for limitations of using prognostic indices in treatment decisions.

## Browser application

Open the GitHub Pages link above, or serve the repository locally:

```bash
python -m http.server 8000
# Open http://localhost:8000/ or http://localhost:8000/web/
```

Enter the five parameters, select **Calculate FLIPI**, review the score and the component breakdown, or download a plain-text summary. All calculations take place directly in the browser with JavaScript. **No Pyodide, server, account, build tool, or external dependency is required for the web calculator.** It works at the root Pages URL and under `/web/`.

**Privacy:** The browser calculator does not send inputs to a server, log them, or persist them to browser storage. Do not enter patient identifiers. Downloaded text summaries are saved to the local device.

## Python CLI

Python 3.10+; the core scoring and batch commands use the standard library.

```bash
python cli.py single --age 65 --stage 4 --hemoglobin 11.5 --ldh-ratio 1.2 --nodal-sites 5
python cli.py batch --input sample.csv --output results.csv
```

Required CSV headers: `age,stage,hemoglobin,ldh_ratio,nodal_sites`. Extra identifier columns can be retained, but use **non-identifying sample keys**, not patient information. Invalid rows return an `ERROR:` cell rather than being silently scored. Exported untrusted text is escaped to reduce spreadsheet formula injection risk.

The optional legacy supervisor commands remain available:

```bash
python cli.py audit --task-id EXAMPLE-01
python cli.py chat "Explain the implementation"
python cli.py verify-audit
```

They require Pydantic, and the supervisory chat uses a **deterministic mock**; it does not perform clinical inference. The generic audit workers are not validated clinical FLIPI decision rules.

## API / Docker

For the optional Python API:

```bash
python -m pip install fastapi uvicorn pydantic
uvicorn agents.api:app --host 127.0.0.1 --port 8000
```

Send JSON to `POST /api/flipi` using keys `age`, `stage`, `hemoglobin`, `ldh_ratio` and `nodal_sites`; view generated API documentation at `/docs`. Other existing endpoints include `/health`, `/metrics`, `/api/audit`, `/api/chat` and `/api/audit/logs`.

```bash
docker compose up --build
# API at http://localhost:8000
```

The optional audit trail is **in-memory**: its HMAC verifies the integrity of the current process's stored entries, not persistence across restarts or independent regulatory compliance. Set `AUDIT_SECRET_KEY` through a secure external secret mechanism when stable signing keys are required; otherwise a random per-process key is used. Do not submit protected health information to the demonstration audit/chat API.

## Tests and compatibility

```bash
python -m pip install pytest fastapi pydantic
pytest -v
node --test web/flipi.test.cjs
```

GitHub Actions runs Python 3.10–3.12 tests, Python compilation, and Node 20 browser-logic tests; the production Pages site is deployed from `master` following successful checks. The static interface targets current Chrome, Firefox, Safari and Edge with standard ECMAScript and DOM APIs; it does not require cookies or local storage.

## License

[MIT](LICENSE). Educational/research decision support; not a substitute for independent clinical evaluation.
