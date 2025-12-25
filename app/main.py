# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware # Don't forget imports
import asyncio

# Ensure these imports match your file structure
from adk_runner import run_triage_planner 
from perception import extract_clinical_data
from hospital_state import hospital_state
from executor import vertex_execute_plan

app = FastAPI(
    title="MediFlow API",
    description="Agentic Smart-Triage System for Emergency Rooms",
    version="1.0.0"
)

# ... CORS config ...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/triage")
async def triage(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()

    # 1. Perception
    clinical_data = extract_clinical_data(audio_bytes)

    # 2. ADK Planning Agent
    triage_plan = await run_triage_planner(
        clinical_data=clinical_data, 
        hospital_state=hospital_state
    )

    # 3. Execution (✅ FIXED HERE)
    # You must pass 'hospital_state' because the function expects it
    execution_result = vertex_execute_plan(triage_plan, hospital_state)

    return {
        "clinical_data": clinical_data,
        "triage_plan": triage_plan,
        "execution_result": execution_result
    }