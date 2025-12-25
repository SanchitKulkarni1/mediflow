from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EXTRACTION_PROMPT = """
You are a clinical extraction system.

Ignore greetings and small talk.
Extract only medically relevant information.

Output STRICT JSON ONLY:
{
  "symptoms": [],
  "vitals": {},
  "provisional_diagnosis": "",
  "clinician_indicated_urgency": "stable|moderate|critical",
  "requested_resources": []
}
"""

def extract_clinical_data(audio_bytes: bytes):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            EXTRACTION_PROMPT,
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm")
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    return json.loads(response.text)
