import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from app.services.commentary import CommentaryService
from app.services.chatbot import ChatbotService
from app.services.tts import TTSService

app = FastAPI(title="DugOut Live Radio")

# Initialize services
commentary_service = CommentaryService()
chatbot_service = ChatbotService()
tts_service = TTSService()

# WebSocket client manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Handle broken connections silently
                pass

manager = ConnectionManager()

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# HTML index route
@app.get("/")
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "DugOut Live Radio API is running. static/index.html is missing."}

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/api/state")
async def get_state():
    return commentary_service.get_state()

class TTSRequest(BaseModel):
    text: str
    persona: str

@app.post("/api/tts")
async def generate_tts(request: TTSRequest):
    audio_bytes = tts_service.generate_audio(request.text, request.persona)
    if audio_bytes:
        return Response(content=audio_bytes, media_type="audio/mpeg")
    return Response(status_code=500, content="Failed to generate audio")

@app.websocket("/api/match/ball")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # Send initial state on connection
    initial_state = commentary_service.get_state()
    initial_state["type"] = "init"
    await websocket.send_text(json.dumps(initial_state))
    
    try:
        while True:
            # Wait for messages from client (e.g., to trigger a ball or change settings)
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            action = payload.get("action")
            persona = payload.get("persona", "Ravi Shastri")
            match_id = payload.get("matchId")
            print(f"DEBUG: WebSocket message received. Action: {action}, Persona: {persona}, Match ID: {match_id}")
            
            if action == "simulate":
                # Fetch ball event (from live API or simulator fallback)
                new_state = commentary_service.fetch_live_ball(match_id)
                print(f"DEBUG: commentary_service.fetch_live_ball result: {new_state}")
                # Translate with AI chatbot
                raw_commentary = new_state["raw_commentary"]
                event_type = new_state["last_event"]
                
                ai_commentary = chatbot_service.translate_to_persona(persona, raw_commentary, event_type)
                
                # Prepare message package
                broadcast_payload = {
                    "type": "ball_event",
                    "score": new_state["score"],
                    "overs": new_state["overs"],
                    "batsman": new_state["batsman"],
                    "non_striker": new_state["non_striker"],
                    "bowler": new_state["bowler"],
                    "last_event": new_state["last_event"],
                    "raw_commentary": raw_commentary,
                    "ai_commentary": ai_commentary,
                    "persona": persona,
                    "is_real_api": new_state.get("is_real_api", False),
                    "team_name": new_state.get("team_name", "IND")
                }
                
                # Broadcast ball event to all connected sockets
                await manager.broadcast(broadcast_payload)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
