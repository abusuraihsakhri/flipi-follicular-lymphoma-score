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
    # Validate
    if age < 0:
        raise ValueError("Age must be non-negative")
    if stage < 1 or stage > 4:
        raise ValueError(f"Ann Arbor stage must be 1-4, got {stage}")
    if hemoglobin < 0:
        raise ValueError("Hemoglobin must be non-negative")
    if ldh_ratio < 0:
        raise ValueError("LDH ratio must be non-negative")
    if nodal_sites < 0:
        raise ValueError("Nodal sites must be non-negative")

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
    """Generate clinical recommendation based on FLIPI risk group."""
    if group == "Low":
        return (
            "Low-risk follicular lymphoma. Excellent long-term prognosis "
            "(10-year OS ~71%). Observation (watch and wait) appropriate for "
            "asymptomatic patients. When treatment needed: rituximab ± chemotherapy. "
            "Consider rituximab monotherapy for low tumor burden."
        )
    elif group == "Intermediate":
        return (
            "Intermediate-risk follicular lymphoma. Moderate prognosis "
            "(10-year OS ~51%). Treatment based on symptoms and tumor burden. "
            "First-line: R-CHOP, R-bendamustine, or R-CVP. "
            "Rituximab maintenance may improve progression-free survival. "
            "Consider clinical trial enrollment."
        )
    else:
        return (
            "High-risk follicular lymphoma. Guarded prognosis "
            "(10-year OS ~36%). Early treatment recommended. "
            "First-line: R-CHOP or R-bendamustine with rituximab maintenance. "
            "Consider autologous stem cell transplant in first remission. "
            "PI3K inhibitors, lenalidomide, or bispecific antibodies for relapsed disease. "
            "Monitor for transformation to aggressive lymphoma. "
            "Clinical trial enrollment strongly encouraged."
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

    out_fields = fieldnames + [
        "flipi_score", "flipi_risk_group", "five_year_survival_pct",
        "ten_year_survival_pct", "clinical_recommendation",
    ]
    out_rows = []
    for r in rows:
        try:
            res = calculate_flipi(
                age=int(r["age"]),
                stage=int(r["stage"]),
                hemoglobin=float(r["hemoglobin"]),
                ldh_ratio=float(r["ldh_ratio"]),
                nodal_sites=int(r["nodal_sites"]),
            )
            row_dict = dict(r)
            row_dict["flipi_score"] = res["flipi_score"]
            row_dict["flipi_risk_group"] = res["flipi_risk_group"]
            row_dict["five_year_survival_pct"] = res["five_year_survival_pct"]
            row_dict["ten_year_survival_pct"] = res["ten_year_survival_pct"]
            row_dict["clinical_recommendation"] = res["clinical_recommendation"]
        except (ValueError, KeyError) as e:
            row_dict = dict(r)
            row_dict["flipi_score"] = f"ERROR: {e}"
            row_dict["flipi_risk_group"] = ""
            row_dict["five_year_survival_pct"] = ""
            row_dict["ten_year_survival_pct"] = ""
            row_dict["clinical_recommendation"] = ""
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
    elif args.command == "batch":
        process_batch(args.input, args.output)


if __name__ == "__main__":
    main()
