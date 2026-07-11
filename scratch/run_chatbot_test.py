import os
from app.services.chatbot import ChatbotService
from dotenv import load_dotenv

load_dotenv()
svc = ChatbotService()
print("Model Name:", svc.model_name)
print("Gemini API Key:", os.getenv("GEMINI_API_KEY")[:10] + "..." if os.getenv("GEMINI_API_KEY") else "None")

raw_event = "37.5: Prabath Jayasuriya to Brandon King, he gets to his half-century in remarkable style, drops it short outside off, King goes deep into the crease and heaves it across the line over deep square leg for FOUR!"
event_type = "Boundary Four"

print("\n--- Ravi Shastri Commentary ---")
print(svc.translate_to_persona("Ravi Shastri", raw_event, event_type))

print("\n--- Virender Sehwag Commentary ---")
print(svc.translate_to_persona("Virender Sehwag", raw_event, event_type))
