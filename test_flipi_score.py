#!/usr/bin/env python3
"""Tests for FLIPI (Follicular Lymphoma International Prognostic Index) - 20 real clinical tests."""

import json
import pytest
from flipi_score import (
    calculate_flipi,
    process_batch,
    _risk_group,
    FLIPI_SURVIVAL_10Y,
    FLIPI_SURVIVAL_5Y,
)


# ---------------------------------------------------------------------------
# Individual risk factor scoring
# ---------------------------------------------------------------------------

class TestRiskFactors:
    def test_age_over_60(self):
        """Age >60 contributes 1 point."""
        res = calculate_flipi(age=65, stage=1, hemoglobin=13.0, ldh_ratio=0.8, nodal_sites=2)
        assert res["risk_factors"]["age_over_60"]["point"] == 1
        assert res["flipi_score"] == 1

    def test_age_exactly_60(self):
        """Age exactly 60 does NOT contribute."""
        res = calculate_flipi(age=60, stage=1, hemoglobin=13.0, ldh_ratio=0.8, nodal_sites=2)
        assert res["risk_factors"]["age_over_60"]["point"] == 0
        assert res["flipi_score"] == 0

    def test_stage_iii(self):
        """Stage III contributes 1 point."""
        res = calculate_flipi(age=50, stage=3, hemoglobin=13.0, ldh_ratio=0.8, nodal_sites=2)
        assert res["risk_factors"]["stage_iii_iv"]["point"] == 1
        assert res["flipi_score"] == 1

    def test_stage_ii_no_point(self):
        """Stage II does NOT contribute."""
        res = calculate_flipi(age=50, stage=2, hemoglobin=13.0, ldh_ratio=0.8, nodal_sites=2)
        assert res["risk_factors"]["stage_iii_iv"]["point"] == 0

    def test_hemoglobin_low(self):
        """Hemoglobin <12 contributes 1 point."""
        res = calculate_flipi(age=50, stage=1, hemoglobin=10.5, ldh_ratio=0.8, nodal_sites=2)
        assert res["risk_factors"]["hemoglobin_low"]["point"] == 1
        assert res["flipi_score"] == 1

    def test_hemoglobin_normal(self):
        """Hemoglobin 12.0 does NOT contribute (must be <12)."""
        res = calculate_flipi(age=50, stage=1, hemoglobin=12.0, ldh_ratio=0.8, nodal_sites=2)
        assert res["risk_factors"]["hemoglobin_low"]["point"] == 0

    def test_ldh_elevated(self):
        """LDH >1.0 contributes 1 point."""
        res = calculate_flipi(age=50, stage=1, hemoglobin=13.0, ldh_ratio=1.5, nodal_sites=2)
        assert res["risk_factors"]["ldh_elevated"]["point"] == 1
        assert res["flipi_score"] == 1

    def test_ldh_normal(self):
        """LDH exactly 1.0 does NOT contribute."""
        res = calculate_flipi(age=50, stage=1, hemoglobin=13.0, ldh_ratio=1.0, nodal_sites=2)
        assert res["risk_factors"]["ldh_elevated"]["point"] == 0

    def test_nodal_sites_gt_4(self):
        """Nodal sites >4 contributes 1 point."""
        res = calculate_flipi(age=50, stage=1, hemoglobin=13.0, ldh_ratio=0.8, nodal_sites=5)
        assert res["risk_factors"]["nodal_sites_gt_4"]["point"] == 1
        assert res["flipi_score"] == 1

    def test_nodal_sites_exactly_4(self):
        """Exactly 4 nodal sites does NOT contribute (must be >4)."""
        res = calculate_flipi(age=50, stage=1, hemoglobin=13.0, ldh_ratio=0.8, nodal_sites=4)
        assert res["risk_factors"]["nodal_sites_gt_4"]["point"] == 0


# ---------------------------------------------------------------------------
# Risk groups
# ---------------------------------------------------------------------------

class TestRiskGroups:
    def test_score_0_low(self):
        assert _risk_group(0) == "Low"

    def test_score_1_low(self):
        assert _risk_group(1) == "Low"

    def test_score_2_intermediate(self):
        assert _risk_group(2) == "Intermediate"

    def test_score_3_high(self):
        assert _risk_group(3) == "High"

    def test_score_5_high(self):
        assert _risk_group(5) == "High"


# ---------------------------------------------------------------------------
# Full FLIPI calculations
# ---------------------------------------------------------------------------

class TestFullFLIPI:
    def test_score_0_low_risk(self):
        """Young, all normal → FLIPI 0, Low risk."""
        res = calculate_flipi(age=45, stage=1, hemoglobin=14.0, ldh_ratio=0.9, nodal_sites=2)
        assert res["flipi_score"] == 0
        assert res["flipi_risk_group"] == "Low"
        assert res["ten_year_survival_pct"] == 71.0

    def test_score_5_high_risk(self):
        """All risk factors → FLIPI 5, High risk."""
        res = calculate_flipi(age=70, stage=4, hemoglobin=10.0, ldh_ratio=2.0, nodal_sites=6)
        assert res["flipi_score"] == 5
        assert res["flipi_risk_group"] == "High"
        assert res["ten_year_survival_pct"] == 36.0

    def test_score_2_intermediate(self):
        """2 risk factors → Intermediate."""
        res = calculate_flipi(age=65, stage=1, hemoglobin=13.0, ldh_ratio=0.8, nodal_sites=2)
        assert res["flipi_score"] == 1  # only age
        # Need 2 factors
        res2 = calculate_flipi(age=65, stage=4, hemoglobin=13.0, ldh_ratio=0.8, nodal_sites=2)
        assert res2["flipi_score"] == 2
        assert res2["flipi_risk_group"] == "Intermediate"

    def test_survival_decreases_with_risk(self):
        """Higher risk → lower survival."""
        low = calculate_flipi(age=45, stage=1, hemoglobin=14.0, ldh_ratio=0.9, nodal_sites=2)
        high = calculate_flipi(age=70, stage=4, hemoglobin=10.0, ldh_ratio=2.0, nodal_sites=6)
        assert low["ten_year_survival_pct"] > high["ten_year_survival_pct"]
        assert low["five_year_survival_pct"] > high["five_year_survival_pct"]

    def test_classification_string(self):
        res = calculate_flipi(age=45, stage=1, hemoglobin=14.0, ldh_ratio=0.9, nodal_sites=2)
        assert "FLIPI" in res["classification"]
        assert "Low" in res["classification"]

    def test_has_recommendation(self):
        res = calculate_flipi(age=45, stage=1, hemoglobin=14.0, ldh_ratio=0.9, nodal_sites=2)
        assert len(res["clinical_recommendation"]) > 10

    def test_risk_factors_count(self):
        res = calculate_flipi(age=65, stage=4, hemoglobin=10.0, ldh_ratio=2.0, nodal_sites=6)
        assert res["risk_factors_count"] == 5


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_negative_age(self):
        with pytest.raises(ValueError):
            calculate_flipi(age=-1, stage=1, hemoglobin=14.0, ldh_ratio=1.0, nodal_sites=2)

    def test_invalid_stage(self):
        with pytest.raises(ValueError):
            calculate_flipi(age=50, stage=5, hemoglobin=14.0, ldh_ratio=1.0, nodal_sites=2)

    def test_negative_hemoglobin(self):
        with pytest.raises(ValueError):
            calculate_flipi(age=50, stage=1, hemoglobin=-1.0, ldh_ratio=1.0, nodal_sites=2)


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

class TestBatch:
    def test_batch_basic(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "age,stage,hemoglobin,ldh_ratio,nodal_sites\n"
            "45,1,14.0,0.9,2\n"
            "70,4,10.0,2.0,6\n",
            encoding="utf-8",
        )
        count = process_batch(str(csv_in), str(csv_out))
        assert count == 2
        assert csv_out.exists()
        content = csv_out.read_text(encoding="utf-8")
        assert "flipi_score" in content
        assert "flipi_risk_group" in content
