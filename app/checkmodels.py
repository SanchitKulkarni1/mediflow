from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# List all available models
for model in client.models.list():
    print(f"Model: {model.name}")
    print(f"Display Name: {model.display_name}")
    # print(f"Supported Methods: {model.supported_generation_methods}")
    print("---")