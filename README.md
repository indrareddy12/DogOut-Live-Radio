# DugOut Live Radio 📻

An interactive cricket AI commentary dashboard featuring custom commentator personas (Ravi Shastri, Virender Sehwag, and Harbhajan Singh). It simulates a live cricket match broadcasted over WebSockets, translates events via AI, and converts them to audio using the browser's speech synthesis engine accompanied by an interactive soundwave visualizer.

## Project Structure
```
c:\Users\indra\Desktop\DugOut Live Radio\
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI Application & WebSocket Endpoint
│   └── services/
│       ├── __init__.py
│       ├── commentary.py       # Commentary Database & State Simulator
│       └── chatbot.py          # AI Translator & Persona Manager
├── static/
│   ├── index.html              # Dashboard User Interface
│   ├── css/
│   │   └── styles.css          # Glassmorphism Design & Wave Animations
│   └── js/
│       └── app.js              # WebSocket Client, TTS engine, and Visualizer controller
├── tests/
│   ├── __init__.py
│   └── test_chatbot.py         # Unit Tests
├── .env                        # Configuration parameters
├── requirements.txt            # Package dependencies
└── README.md
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys (Optional)**:
   Add your Gemini API Key in the `.env` file to fetch genuine translations from LLM. If left empty, it runs using the offline template fallback library.
   ```env
   GEMINI_API_KEY=your-gemini-key-here
   ```

3. **Start the server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Access UI**:
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
