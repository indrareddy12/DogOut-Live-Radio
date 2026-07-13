# DugOut Live Radio 📻🏏
An interactive cricket AI commentary dashboard featuring custom commentator personas (**Ravi Shastri**, **Virender Sehwag**, and **Harbhajan Singh**). The application streams real-time Cricbuzz live matches, translates ball-by-ball updates via Google Gemini AI into distinct commentator styles, and converts them to speech using ElevenLabs with automated browser-native audio fallbacks. 

---

## 🌟 Key Features

*   ⚡ **Real-Time Cricbuzz Sync**: Connects to the Cricbuzz API via RapidAPI to stream actual match scorecards, overs, batsman/bowler states, and ball-by-ball raw commentaries.
*   🤖 **Google Gemini Persona Engine**: Translates raw events on-the-fly using `gemini-2.5-flash` into Ravi's high-energy exclamations, Sehwag's witty Hinglish humor, or Bhajji's passionate bowling analysis.
*   🎙️ **ElevenLabs Audio Streaming**: Automatically generates realistic voice readouts using ElevenLabs' high-fidelity `eleven_turbo_v2_5` low-latency model.
*   🔊 **Browser-Native TTS Fallback**: If ElevenLabs credits are exhausted or credentials are missing, the UI automatically falls back to browser-native `SpeechSynthesis` with custom pitches/speeds calibrated for each commentator.
*   🎨 **Premium Glassmorphism UI**: A dark-mode, glassmorphism interface featuring responsive widgets and a dynamic soundwave visualizer synced with the audio output.
*   🧪 **Passing Test Suite**: Robust test suite mocking API credentials and verifying commentator fallbacks, making it ready for CI/CD.

---

## 📂 Project Structure

```
DugOut-Live-Radio/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI Application & WebSocket Endpoint
│   └── services/
│       ├── __init__.py
│       ├── commentary.py       # Cricbuzz API sync & match simulator
│       ├── chatbot.py          # Gemini AI translator & persona prompts
│       └── tts.py              # ElevenLabs Text-to-Speech service
├── static/
│   ├── index.html              # Dashboard User Interface (Glassmorphism)
│   ├── css/
│   │   └── styles.css          # Dark-theme layout & visualizer wave keyframes
│   └── js/
│       └── app.js              # WebSocket connection, Web Speech Fallback, Visualizer
├── tests/
│   ├── __init__.py
│   ├── test_chatbot.py         # Chatbot persona & fallback unit tests
│   └── test_commentary.py      # Commentary service & simulator unit tests
├── .env.example                # Sample environment configuration file
├── requirements.txt            # Package dependencies
└── README.md
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.10+ installed. Clone the repository and install the dependencies:
```bash
git clone https://github.com/indrareddy12/DogOut-Live-Radio.git
cd DogOut-Live-Radio
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root folder (or rename `.env.example` if available):
```env
# Gemini API Key (Required for live AI translation)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-flash

# RapidAPI configuration (for live Cricbuzz match data)
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com
CRICKET_MATCH_ID=152427

# ElevenLabs configuration (for commentary audio)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
VOICE_ID_RAVI=
VOICE_ID_SEHWAG=
VOICE_ID_HARBHAJAN=
```

---

## 🎙️ Note on ElevenLabs Voice Cloning

To run out-of-the-box on the **ElevenLabs Free Tier**:
*   Leave the `VOICE_ID_RAVI`, `VOICE_ID_SEHWAG`, and `VOICE_ID_HARBHAJAN` parameters **blank** (or omit them).
*   The application will automatically use ElevenLabs' high-quality premade voices (**Charlie** for Shastri, **Roger** for Sehwag, and **Chris** for Harbhajan).

### To Use the Exact Cricketers' Cloned Voices:
1. ElevenLabs restricts Instant Voice Cloning (creating a custom voice from uploaded audio clips) to their paid tiers starting with the **Starter plan ($6/month)**.
2. If subscribed, upload a 1-2 minute clean audio sample of each cricketer in your ElevenLabs account.
3. Copy the generated Voice IDs from your ElevenLabs Voice Lab and update your `.env` file accordingly.

---

## 🚀 Running the Application

1. **Start the FastAPI Backend**:
   ```bash
   python -m uvicorn app.main:app --port 8088
   ```

2. **Access the Dashboard**:
   Open [http://localhost:8088](http://localhost:8088) in your web browser.

3. **Interact**:
   Select a commentator, toggle **Listen Live Radio** ON, and click **Simulate Next Ball** to trigger live ball commentary and speech output.

---

## 🧪 Running Unit Tests
To run the automated test suite locally and verify all mocks and service fallbacks:
```bash
python -m pytest -v
```
All tests should pass successfully.
