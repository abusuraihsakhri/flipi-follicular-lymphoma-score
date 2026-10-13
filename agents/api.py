"""
FastAPI REST API Server for Flipi Follicular Lymphoma Score.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .base import AuditLogger, PHIGuard, SecurityException
from flipi_score import calculate_flipi
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Flipi Follicular Lymphoma Score API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class FlipiRequest(BaseModel):
    age: int = Field(ge=0, strict=True)
    stage: int = Field(ge=1, le=4, strict=True)
    hemoglobin: float = Field(ge=0, allow_inf_nan=False)
    ldh_ratio: float = Field(ge=0, allow_inf_nan=False)
    nodal_sites: int = Field(ge=0, strict=True)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "flipi-follicular-lymphoma-score", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.post("/api/flipi")
def api_flipi(payload: FlipiRequest):
    """Stateless classical FLIPI score; no identifying patient data accepted."""
    return calculate_flipi(**payload.model_dump())


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
        return dossier.to_dict()
    except SecurityException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
