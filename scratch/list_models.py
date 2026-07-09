import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
url = "https://api.elevenlabs.io/v1/models"
headers = {"xi-api-key": api_key}
res = requests.get(url, headers=headers)
print("Status:", res.status_code)
for model in res.json():
    print(f"ID: {model['model_id']}, Name: {model['name']}")
