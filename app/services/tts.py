import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TTSService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
        # Placeholder Voice IDs for the personas.
        # The user will need to replace these with actual cloned voice IDs from their ElevenLabs account.
        self.voice_map = {
            "Ravi Shastri": os.getenv("VOICE_ID_RAVI", "pNInz6obbfDQGcgMyIGC"), # Example default IDs
            "Virender Sehwag": os.getenv("VOICE_ID_SEHWAG", "ErXwobaYiN019PkySvjV"),
            "Harbhajan Singh": os.getenv("VOICE_ID_HARBHAJAN", "VR6AewLTigWG4xSOukaG")
        }
        
    def generate_audio(self, text: str, persona: str) -> bytes:
        if not self.api_key:
            print("WARNING: ELEVENLABS_API_KEY is not set. Cannot generate cloned audio.")
            return b""
            
        voice_id = self.voice_map.get(persona)
        if not voice_id:
            # Fallback to a default voice
            voice_id = "pNInz6obbfDQGcgMyIGC"
            
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            url = f"{self.base_url}/{voice_id}"
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"ElevenLabs TTS Error: {e}")
            return b""
