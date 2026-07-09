import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
url = "https://api.elevenlabs.io/v1/voices"
headers = {"xi-api-key": api_key}
res = requests.get(url, headers=headers)
print("Status:", res.status_code)
if res.status_code == 200:
    data = res.json()
    voices = data.get("voices", [])
    for v in voices:
        print(f"ID: {v['voice_id']}, Name: {v['name']}, Category: {v.get('category')}")
