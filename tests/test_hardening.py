"""Regressions for FLIPI input validation, API, batch parsing, and audit integrity."""
import csv
import math

import pytest

from flipi_score import calculate_flipi, process_batch
from agents.api import FlipiRequest, api_flipi
from agents.base import AuditTrail
from agents.llm_factory import LLMFactory


PARAMS = dict(age=60, stage=2, hemoglobin=12.0, ldh_ratio=1.0, nodal_sites=4)


@pytest.mark.parametrize("field,value", [
    ("age", 60.1), ("age", True), ("age", -1), ("stage", 2.5),
    ("stage", 0), ("stage", 5), ("nodal_sites", 2.2),
    ("nodal_sites", False), ("hemoglobin", float("nan")),
    ("hemoglobin", float("inf")), ("hemoglobin", -1.0),
    ("ldh_ratio", float("-inf")), ("ldh_ratio", float("nan")),
    ("ldh_ratio", -0.1), ("ldh_ratio", False),
])
def test_invalid_scoring_inputs_rejected(field, value):
    with pytest.raises(ValueError):
        calculate_flipi(**{**PARAMS, field: value})


def test_original_cutoffs_and_neutral_prognostic_guidance():
    assert calculate_flipi(**PARAMS)["flipi_score"] == 0
    high = calculate_flipi(age=61, stage=4, hemoglobin=11,
                           ldh_ratio=1.1, nodal_sites=5)
    assert high["flipi_score"] == 5
    assert high["flipi_risk_group"] == "High"
    assert "does not establish the need for treatment" in high["clinical_recommendation"]
    assert "transplant" not in high["clinical_recommendation"].lower()


def test_validated_fastapi_scoring():
    result = api_flipi(FlipiRequest(**PARAMS))
    assert result["flipi_score"] == 0
    with pytest.raises(Exception):
        FlipiRequest(**{**PARAMS, "stage": 5})


def test_batch_requires_columns(tmp_path):
    source = tmp_path / "missing.csv"
    source.write_text("age,stage\n60,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        process_batch(str(source), str(tmp_path / "out.csv"))


def test_batch_bad_rows_and_csv_formula_safety(tmp_path):
    source = tmp_path / "patients.csv"
    dest = tmp_path / "out.csv"
    source.write_text(
        "patient_key,age,stage,hemoglobin,ldh_ratio,nodal_sites\n"
        "=1+1,60,2,12,1,4\n"
        "key-extra,60,2,12,1,4,unexpected-field\n"
        "key-missing,60,2,12,1\n",
        encoding="utf-8",
    )
    assert process_batch(str(source), str(dest)) == 3
    with dest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["patient_key"].startswith("'=1+1")
    assert rows[0]["flipi_score"] == "0"
    assert rows[1]["flipi_score"].startswith("ERROR:")
    assert rows[2]["flipi_score"].startswith("ERROR:")


def test_audit_checks_signatures_and_prevents_external_mutation():
    trail = AuditTrail("unit-test-secret")
    entry = trail.log("unit-test", "tester", "EVALUATED", {"status": "ok"})
    assert trail.verify_integrity()
    exported = trail.get_trail()
    exported[0]["event_type"] = "forged"
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "forged"
    assert not trail.verify_integrity()


def test_mock_does_not_claim_to_have_verified_analysis():
    reply = LLMFactory.create("mock").invoke("hello")
    assert "No clinical verification" in reply
