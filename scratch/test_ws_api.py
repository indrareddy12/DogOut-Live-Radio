import os
import sys
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.abspath("."))

from app.main import app

load_dotenv()
client = TestClient(app)

print("Connecting to WebSocket...")
with client.websocket_connect("/api/match/ball") as websocket:
    # Receive initial "init" state
    init_data = websocket.receive_json()
    print("Received connection init event.")
    
    print("Sending simulate message...")
    websocket.send_json({
        "action": "simulate",
        "persona": "Ravi Shastri",
        "matchId": "152427"
    })
    
    print("Waiting for ball_event...")
    data = websocket.receive_json()
    print("Received ball_event:")
    print("Score:", data.get("score"))
    print("Overs:", data.get("overs"))
    print("Batsman:", data.get("batsman"))
    print("Raw Commentary:", data.get("raw_commentary"))
    print("AI Commentary:", repr(data.get("ai_commentary")))
