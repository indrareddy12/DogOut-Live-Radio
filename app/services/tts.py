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
            "Ravi Shastri": os.getenv("VOICE_ID_RAVI", "IKne3meq5aSn9XLyUdCD"), 
            "Virender Sehwag": os.getenv("VOICE_ID_SEHWAG", "CwhRBWXzGAHq8TQ4Fs17"),
            "Harbhajan Singh": os.getenv("VOICE_ID_HARBHAJAN", "iP95p4xoKVk53GoZ742B")
        }
        
    def generate_audio(self, text: str, persona: str) -> bytes:
        if not self.api_key or self.api_key.startswith("your_"):
            print("WARNING: ELEVENLABS_API_KEY is not set or is a placeholder. Cannot generate audio.")
            return b""
            
        voice_id = self.voice_map.get(persona)
        if not voice_id or voice_id.startswith("your_") or "voice_id_here" in voice_id:
            # Fallback to active default premade voice IDs (compatible with Free tier)
            default_voices = {
                "Ravi Shastri": "IKne3meq5aSn9XLyUdCD",     # Charlie (Deep, Confident, Energetic)
                "Virender Sehwag": "CwhRBWXzGAHq8TQ4Fs17",  # Roger (Laid-Back, Casual, Resonant)
                "Harbhajan Singh": "iP95p4xoKVk53GoZ742B"   # Chris (Charming, Down-to-Earth)
            }
            voice_id = default_voices.get(persona, "IKne3meq5aSn9XLyUdCD")
            
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
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
