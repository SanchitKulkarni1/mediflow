# app/agents/triage_planner_agent.py
from google.adk.agents import Agent
from google.genai.types import GenerateContentConfig

PLANNING_PROMPT = """
You are a triage planning agent.

Your task is to generate a TRIAGE EXECUTION PLAN.

You MUST output JSON in EXACTLY this format:

{
  "priority": "HIGH | MEDIUM | LOW",
  "actions": [
    {
      "type": "BOOK_LAB",
      "resource": "<lab_name>"
    }
  ]
}

Rules:
- Output ONLY valid JSON
- ALWAYS include "actions" (empty list allowed)
- Do NOT add extra keys
- Do NOT explain anything
- Respect clinician_indicated_urgency
"""


TriagePlannerAgent = Agent(
    name="TriagePlannerAgent",
    model="gemini-2.5-flash",
    instruction=PLANNING_PROMPT,  # Now strictly static
    generate_content_config=GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2
    )
)