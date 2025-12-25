# app/agents/triage_planner_agent.py

from adk import Agent
from google import genai
import os, json

# Gemini client for reasoning
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def planning_logic(inputs: dict) -> dict:
    """
    ADK Planning Agent Logic
    - Side-effect free
    - Reasoning only
    """

    prompt = f"""
You are a triage planning agent.

Clinical data:
{json.dumps(inputs['clinical_data'], indent=2)}

Hospital state:
{json.dumps(inputs['hospital_state'], indent=2)}

Rules:
- Do NOT execute actions
- Do NOT decide medical urgency
- Respect clinician_indicated_urgency
- Output ONLY valid JSON

Output format:
{{
  "priority": "HIGH|MEDIUM|LOW",
  "actions": [
    {{
      "type": "BOOK_LAB|BOOK_IMAGING",
      "resource": "string",
      "deadline": "string"
    }}
  ],
  "justification": "string"
}}
"""

    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    )

    return json.loads(response.text)


# ✅ ADK Agent definition
TriagePlannerAgent = Agent(
    name="TriagePlannerAgent",
    description="Agentic triage planning agent",
    run=planning_logic
)
