from fastapi import FastAPI, UploadFile, File
from perception import extract_clinical_data
from hospital_state import hospital_state
from executor import vertex_execute_plan
from agents.triage_planner_agent import TriagePlannerAgent

app = FastAPI()

@app.post("/triage")
async def triage(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()

    # 1. Perception (Gemini API)
    clinical_data = extract_clinical_data(audio_bytes)

    # 2. ADK Planning Agent
    triage_plan = TriagePlannerAgent.run({
        "clinical_data": clinical_data,
        "hospital_state": hospital_state
    })

    # 3. Vertex AI Execution
    execution_result = vertex_execute_plan(triage_plan)

    return {
        "clinical_data": clinical_data,
        "triage_plan": triage_plan,
        "execution_result": execution_result
    }
