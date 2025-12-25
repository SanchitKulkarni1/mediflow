# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from adk_runner import run_triage_planner
from perception import extract_clinical_data
from hospital_state import hospital_state
from executor import vertex_execute_plan, approve_preemption
from audit_log import AUDIT_LOG

app = FastAPI(
    title="MediFlow API",
    description="Agentic Smart-Triage System for Emergency Rooms",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Core triage endpoint
# -------------------------
@app.post("/triage")
async def triage(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()

    clinical_data = extract_clinical_data(audio_bytes)

    triage_plan = await run_triage_planner(
        clinical_data=clinical_data,
        hospital_state=hospital_state
    )

    execution_result = vertex_execute_plan(triage_plan, hospital_state)

    return {
        "clinical_data": clinical_data,
        "triage_plan": triage_plan,
        "execution_result": execution_result
    }

# -------------------------
# Audit trail
# -------------------------
@app.get("/audit-log")
def get_audit_log():
    return {
        "events": AUDIT_LOG
    }

# -------------------------
# Doctor approval endpoint
# -------------------------
@app.post("/approve-preemption")
def approve_preemption_endpoint(
    request_id: str,
    resource: str,
    incoming_priority: str
):
    return approve_preemption(
        request_id=request_id,
        resource=resource,
        incoming_priority=incoming_priority,
        hospital_state=hospital_state
    )
