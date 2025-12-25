# app/adk_runner.py
import json
from google.adk.runners import InMemoryRunner
from google.genai import types
from agents.triage_planner_agent import TriagePlannerAgent


async def run_triage_planner(clinical_data: dict, hospital_state: dict) -> dict:
    # 1. Initialize Runner
    runner = InMemoryRunner(
        agent=TriagePlannerAgent,
        app_name="Mediflow"
    )

    # 2. Create Session
    session = await runner.session_service.create_session(
        app_name="Mediflow",
        user_id="generic-user"
    )

    # 3. Format Input
    agent_input = f"""
Analyze this case.

Clinical Data:
{clinical_data}

Hospital State:
{hospital_state}
"""

    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=agent_input)]
    )

    # 4. Run Agent
    response_text = ""
    async for event in runner.run_async(
        user_id="generic-user",
        session_id=session.id,
        new_message=user_message
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    # 5. Parse and enforce contract
    try:
        plan = json.loads(response_text)

        # HARD CONTRACT ENFORCEMENT
        if not isinstance(plan, dict):
            raise ValueError("Planner output is not a JSON object")

        if "actions" not in plan or not isinstance(plan["actions"], list):
            plan["actions"] = []

        if "priority" not in plan:
            plan["priority"] = "LOW"

        return plan

    except Exception as e:
        print("❌ Planner output error:", e)
        print("❌ Raw planner output:", response_text)

        return {
            "priority": "LOW",
            "actions": [],
            "error": "Planner returned invalid JSON"
        }
