import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = "pNInz6obpgDQGcFmaJgB"
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}
data = {
    "text": "Hello world, this is a test.",
    "model_id": "eleven_turbo_v2_5",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}
res = requests.post(url, json=data, headers=headers)
print("Status:", res.status_code)
print("Body:", res.text)
