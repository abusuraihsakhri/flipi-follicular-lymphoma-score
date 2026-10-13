#!/usr/bin/env python3
"""
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
"""

import argparse
import csv
import json
import sys
import math
import numbers
from typing import Dict, Any, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# 10-year overall survival by FLIPI risk group (%)
FLIPI_SURVIVAL_10Y = {
    "Low": 71.0,
    "Intermediate": 51.0,
    "High": 36.0,
}

# 5-year overall survival by FLIPI risk group (%)
FLIPI_SURVIVAL_5Y = {
    "Low": 91.0,
    "Intermediate": 78.0,
    "High": 53.0,
}


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

def calculate_flipi(
    age: int,
    stage: int,
    hemoglobin: float,
    ldh_ratio: float,
    nodal_sites: int,
) -> Dict[str, Any]:
    """
    Calculate FLIPI score for follicular lymphoma.

    Parameters:
        age: Patient age in years
        stage: Ann Arbor stage (1-4)
        hemoglobin: Hemoglobin level in g/dL
        ldh_ratio: LDH / upper limit of normal (e.g., 1.5 means 1.5x ULN)
        nodal_sites: Number of involved nodal sites

    Returns:
        Dict with FLIPI score, risk group, survival estimates, and details.
    """
    # Guard against booleans, fractional counts, NaN, and infinities. These
    # otherwise pass some numeric comparisons and can silently change scoring.
    for name, value in (("Age", age), ("Ann Arbor stage", stage),
                        ("Nodal sites", nodal_sites)):
        if isinstance(value, bool) or not isinstance(value, numbers.Integral):
            raise ValueError(f"{name} must be an integer")
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
    if stage < 1 or stage > 4:
        raise ValueError(f"Ann Arbor stage must be 1-4, got {stage}")
    for name, value in (("Hemoglobin", hemoglobin), ("LDH ratio", ldh_ratio)):
        if isinstance(value, bool) or not isinstance(value, numbers.Real):
            raise ValueError(f"{name} must be a finite number")
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and non-negative")

    # Score each factor
    factors = {}
    score = 0

    # Age > 60
    age_point = 1 if age > 60 else 0
    factors["age_over_60"] = {"value": age, "point": age_point}
    score += age_point

    # Stage III-IV
    stage_point = 1 if stage >= 3 else 0
    factors["stage_iii_iv"] = {"value": stage, "point": stage_point}
    score += stage_point

    # Hemoglobin < 12 g/dL
    hgb_point = 1 if hemoglobin < 12.0 else 0
    factors["hemoglobin_low"] = {"value_g_dl": hemoglobin, "point": hgb_point}
    score += hgb_point

    # LDH > normal
    ldh_point = 1 if ldh_ratio > 1.0 else 0
    factors["ldh_elevated"] = {"ratio": ldh_ratio, "point": ldh_point}
    score += ldh_point

    # Nodal sites > 4
    nodal_point = 1 if nodal_sites > 4 else 0
    factors["nodal_sites_gt_4"] = {"count": nodal_sites, "point": nodal_point}
    score += nodal_point

    # Risk group
    risk_group = _risk_group(score)

    return {
        "tool": "flipi-follicular-lymphoma-score",
        "flipi_score": score,
        "flipi_risk_group": risk_group,
        "five_year_survival_pct": FLIPI_SURVIVAL_5Y[risk_group],
        "ten_year_survival_pct": FLIPI_SURVIVAL_10Y[risk_group],
        "risk_factors": factors,
        "risk_factors_count": score,
        "classification": f"FLIPI {score}/5 - {risk_group} Risk",
        "clinical_recommendation": _recommendation(risk_group, score),
    }


def _risk_group(score: int) -> str:
    """Map FLIPI score to risk group."""
    if score <= 1:
        return "Low"
    elif score == 2:
        return "Intermediate"
    else:
        return "High"


def _recommendation(group: str, score: int) -> str:
    """Return non-prescriptive context: FLIPI is prognostic, not predictive."""
    return (
        f"Classical FLIPI {score}/5 ({group} risk) is a prognostic classification. "
        "Historical 5- and 10-year overall survival figures describe the original "
        "cohort and must not be interpreted as individual contemporary predictions. "
        "FLIPI alone does not establish the need for treatment, select therapy, "
        "or predict treatment response. Management requires clinical assessment "
        "of symptoms, tumor burden, disease course, and patient factors."
    )


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def process_batch(input_csv: str, output_csv: str) -> int:
    """Process a CSV of patients and write FLIPI results."""
    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    required = {"age", "stage", "hemoglobin", "ldh_ratio", "nodal_sites"}
    if len(fieldnames) != len(set(fieldnames)):
        raise ValueError("CSV contains duplicate column names")
    missing = required.difference(fieldnames)
    if missing:
        raise ValueError("CSV missing required columns: " + ", ".join(sorted(missing)))

    # Avoid duplicate output headers if a result CSV is processed again.
    result_columns = [
        "flipi_score", "flipi_risk_group", "five_year_survival_pct",
        "ten_year_survival_pct", "clinical_recommendation",
    ]
    out_fields = [name for name in fieldnames if name not in result_columns] + [
        "flipi_score", "flipi_risk_group", "five_year_survival_pct",
        "ten_year_survival_pct", "clinical_recommendation",
    ]
    out_rows = []
    for r in rows:
        try:
            if None in r or any(value is None for value in r.values()):
                raise ValueError("row has an incorrect number of fields")
            res = calculate_flipi(
                age=int(r["age"]),
                stage=int(r["stage"]),
                hemoglobin=float(r["hemoglobin"]),
                ldh_ratio=float(r["ldh_ratio"]),
                nodal_sites=int(r["nodal_sites"]),
            )
            row_dict = {key: value for key, value in r.items() if key is not None}
            row_dict["flipi_score"] = res["flipi_score"]
            row_dict["flipi_risk_group"] = res["flipi_risk_group"]
            row_dict["five_year_survival_pct"] = res["five_year_survival_pct"]
            row_dict["ten_year_survival_pct"] = res["ten_year_survival_pct"]
            row_dict["clinical_recommendation"] = res["clinical_recommendation"]
        except (ValueError, KeyError, TypeError, OverflowError) as e:
            row_dict = {key: value for key, value in r.items() if key is not None}
            row_dict["flipi_score"] = f"ERROR: {e}"
            row_dict["flipi_risk_group"] = ""
            row_dict["five_year_survival_pct"] = ""
            row_dict["ten_year_survival_pct"] = ""
            row_dict["clinical_recommendation"] = ""
        # Prevent spreadsheet software from interpreting untrusted CSV fields
        # as formulas when exported files are opened.
        for key, value in row_dict.items():
            if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                row_dict[key] = "'" + value
        out_rows.append(row_dict)

    with open(output_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {output_csv}")
    return len(out_rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="FLIPI (Follicular Lymphoma International Prognostic Index)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single evaluation
    sp = subparsers.add_parser("single", help="Evaluate a single FL patient")
    sp.add_argument("--age", type=int, required=True,
                    help="Patient age in years")
    sp.add_argument("--stage", type=int, required=True,
                    help="Ann Arbor stage (1-4)")
    sp.add_argument("--hemoglobin", type=float, required=True,
                    help="Hemoglobin in g/dL")
    sp.add_argument("--ldh-ratio", type=float, required=True,
                    help="LDH / upper limit of normal (e.g., 1.5 for 1.5x ULN)")
    sp.add_argument("--nodal-sites", type=int, required=True,
                    help="Number of involved nodal sites")

    # Batch processing
    bp = subparsers.add_parser("batch", help="Batch process CSV file")
    bp.add_argument("-i", "--input", required=True, help="Input CSV file")
    bp.add_argument("-o", "--output", default="results.csv", help="Output CSV file")

    # Audit dispatch
    ap = subparsers.add_parser("audit", help="Dispatch audit task across workers")
    ap.add_argument("--task-id", required=True, help="Task identifier")

    # Supervisory chat
    cp = subparsers.add_parser("chat", help="Air-gapped supervisory chat")
    cp.add_argument("query", nargs="+", help="Query text")

    # Audit verification
    subparsers.add_parser("verify-audit", help="Verify HMAC audit trail integrity")

    args = parser.parse_args(argv)

    if args.command == "single":
        result = calculate_flipi(
            age=args.age,
            stage=args.stage,
            hemoglobin=args.hemoglobin,
            ldh_ratio=args.ldh_ratio,
            nodal_sites=args.nodal_sites,
        )
        print(json.dumps(result, indent=2))
        return 0
    elif args.command == "batch":
        process_batch(args.input, args.output)
        return 0
    elif args.command == "audit":
        from agents.supervisor import SystemSupervisor
        from agents.models import SystemTaskPayload
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id=args.task_id,
            target_identifier="CLI-TARGET",
            primary_metric=10.0,
            secondary_metric=3.0,
            status_descriptor="NOMINAL",
        )
        dossier = supervisor.process_task(payload)
        print(json.dumps(dossier.to_dict(), indent=2, default=str))
        return 0
    elif args.command == "chat":
        from agents.supervisor import SystemSupervisor
        supervisor = SystemSupervisor(model_provider="mock")
        query = " ".join(args.query)
        response = supervisor.query_supervisory_chat(query)
        print(json.dumps({"response": response}, indent=2))
        return 0
    elif args.command == "verify-audit":
        from agents.base import AuditLogger
        verified = AuditLogger.verify_integrity()
        trail_len = len(AuditLogger.get_trail())
        print(json.dumps({"audit_trail_length": trail_len, "integrity_verified": verified}, indent=2))
        return 0


if __name__ == "__main__":
    main()
