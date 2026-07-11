import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.abspath("."))

from app.services.chatbot import ChatbotService

load_dotenv()
svc = ChatbotService()

events = [
    ("14.3: Shaheen Afridi to Virat Kohli, SIX, what a shot! Over the bowler's head!", "Sixer"),
    ("14.4: Shaheen Afridi to Virat Kohli, no run, solid defense", "Dot Ball"),
    ("14.5: Shaheen Afridi to Virat Kohli, 1 run, tucked away to square leg", "Single")
]

for raw, etype in events:
    print(f"\n========================================\nRaw: {raw}\n========================================")
    print("Ravi Shastri:", svc.translate_to_persona("Ravi Shastri", raw, etype))
    print("Virender Sehwag:", svc.translate_to_persona("Virender Sehwag", raw, etype))
