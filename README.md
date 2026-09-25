# 🏥 MediFlow: Agentic Smart-Triage API for Emergency Rooms

MediFlow turns a **raw audio recording of a doctor–patient conversation** into a **prioritised, executed triage plan**. It extracts the clinical facts, decides urgency, and books the required labs. If there's no free slot, it can **pre-empt lower-priority bookings** after a clinician approves.

Frontend: [flowcare-triage](https://github.com/SanchitKulkarni1/flowcare-triage)

## Architecture

```
audio ──▶ Perception ──▶ Planner agent ──▶ Executor ──▶ Audit log
          (Gemini)       (Google ADK)      (booking + pre-emption)
```

| Stage | File | What it does |
|---|---|---|
| **Perception** | `app/perception.py` | Sends the audio to Gemini 2.5 Flash and extracts strict JSON: symptoms, vitals, provisional diagnosis, clinician-indicated urgency and requested resources. Small talk is ignored. |
| **Planning** | `app/agents/triage_planner_agent.py` | A Google ADK agent combines the clinical data with live hospital state and outputs an execution plan: `priority` (HIGH / MEDIUM / LOW) plus `BOOK_LAB` actions. |
| **Execution** | `app/executor.py` | Books slots. If a lab is full, it compares priority ranks and proposes pre-empting a lower-priority booking, which needs clinician approval. |
| **Audit** | `app/audit_log.py` | Timestamped log of every decision and booking. |

Hospital capacity (troponin, CBC, LFT, KFT, electrolyte panel, dialysis, …) is modelled in `app/hospital_state.py`.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/triage` | Upload audio (`multipart/form-data`, field `audio`) → clinical summary + executed plan |
| `POST` | `/approve-preemption` | Confirm a pending pre-emption |
| `GET` | `/audit-log` | Full decision trail |

Interactive docs are at `/docs` once the server is running.

## Tech stack

Python · FastAPI · Google Gemini 2.5 Flash (audio understanding) · Google Agent Development Kit (ADK)

## Run locally

```bash
pip install -r requirements.txt google-adk google-genai
echo "GEMINI_API_KEY=your_key" > .env
echo "GOOGLE_API_KEY=your_key" >> .env

cd app
uvicorn main:app --reload
```
