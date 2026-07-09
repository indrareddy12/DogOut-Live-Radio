// WebSocket and UI Management
let socket = null;
let currentPersona = "Ravi Shastri";
let autoPlayInterval = null;

// DOM Elements
const scoreVal = document.getElementById("score-val");
const oversVal = document.getElementById("overs-val");
const batsmanVal = document.getElementById("batsman-val");
const nonStrikerVal = document.getElementById("non-striker-val");
const bowlerVal = document.getElementById("bowler-val");
const streamStatus = document.getElementById("stream-status");
const audioWave = document.getElementById("audio-wave");
const speakerNameDisplay = document.getElementById("speaker-name-display");
const connectionIndicator = document.getElementById("connection-indicator");
const feedContainer = document.getElementById("feed-container");
const simulateBtn = document.getElementById("simulate-btn");
const radioToggle = document.getElementById("radio-toggle");
const personaButtons = document.querySelectorAll(".persona-btn");
const matchIdInput = document.getElementById("match-id-input");
const apiBadge = document.getElementById("api-badge");

// Initialize Audio Player for TTS
let currentAudio = null;

// Connect to WebSocket Server
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    socket = new WebSocket(`${protocol}//${host}/api/match/ball`);

    socket.onopen = () => {
        connectionIndicator.textContent = "Connected";
        connectionIndicator.className = "indicator-connected";
    };

    socket.onclose = () => {
        connectionIndicator.textContent = "Disconnected";
        connectionIndicator.className = "indicator-disconnected";
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "init") {
            updateScoreboard(data);
            if (data.default_match_id && !matchIdInput.value) {
                matchIdInput.value = data.default_match_id;
            }
            if (data.is_real_api) {
                apiBadge.textContent = "API ACTIVE";
                apiBadge.className = "api-badge api-realtime";
            } else {
                apiBadge.textContent = "SIMULATOR MODE";
                apiBadge.className = "api-badge api-simulator";
            }
        } else if (data.type === "update") {
            updateScoreboard(data);
            
            if (data.is_real_api) {
                apiBadge.textContent = "API ACTIVE";
                apiBadge.className = "api-badge api-realtime";
            } else {
                apiBadge.textContent = "SIMULATOR MODE";
                apiBadge.className = "api-badge api-simulator";
            }
            
            // Add raw commentary item to feed
            addFeedItem(data.overs, data.last_event || "Event", data.raw_commentary);
        } else if (data.type === "ball_event") {
            updateScoreboard(data);
            appendCommentaryFeed(data);
            
            // Update API Status Badge
            if (data.is_real_api) {
                apiBadge.textContent = "API ACTIVE";
                apiBadge.className = "api-badge api-realtime";
            } else {
                apiBadge.textContent = "SIMULATOR MODE";
                apiBadge.className = "api-badge api-simulator";
            }
            
            // Trigger TTS if Radio is toggled ON
            if (radioToggle.checked && data.ai_commentary) {
                speakCommentary(data.ai_commentary, data.persona);
            }
        }
    };
}

// Update Scoreboard UI
function updateScoreboard(data) {
    scoreVal.textContent = data.score || "0/0";
    oversVal.textContent = data.overs || "0.0";
    batsmanVal.textContent = `${data.batsman || "Batsman"} *`;
    nonStrikerVal.textContent = data.non_striker || "Non-Striker";
    bowlerVal.textContent = data.bowler || "Bowler";
    const teamNameVal = document.getElementById("team-name-val");
    if (teamNameVal) {
        teamNameVal.textContent = data.team_name || "IND";
    }
}

// Append Commentary item to Live Feed
function appendCommentaryFeed(data) {
    // Remove placeholder if present
    const placeholder = feedContainer.querySelector(".feed-placeholder");
    if (placeholder) {
        placeholder.remove();
    }

    const item = document.createElement("div");
    item.className = "commentary-item";

    item.innerHTML = `
        <div class="ball-indicator">
            <span>Over ${data.overs}</span>
            <span class="ball-type">${data.last_event}</span>
        </div>
        <div class="raw-text">${data.raw_commentary}</div>
        <div class="ai-speech-bubble">
            <div class="speaker-header">
                <i class="fa-solid fa-microphone"></i> <span>${data.persona} (AI Live Radio)</span>
            </div>
            <div class="ai-text">${data.ai_commentary}</div>
        </div>
    `;

    feedContainer.prepend(item);

    // Keep only last 15 commentary items to prevent memory bloat
    if (feedContainer.children.length > 15) {
        feedContainer.lastElementChild.remove();
    }
}

// Voice synthesis configuration using ElevenLabs API
async function speakCommentary(text, persona) {
    // Cancel any ongoing speech
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }

    try {
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text, persona })
        });
        
        if (!response.ok) throw new Error("Failed to generate audio");
        
        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);
        
        currentAudio = new Audio(audioUrl);
        
        currentAudio.onplay = () => {
            audioWave.classList.add("active");
            streamStatus.textContent = "ON AIR";
            streamStatus.className = "status-online";
            speakerNameDisplay.textContent = persona;
        };

        currentAudio.onended = () => {
            audioWave.classList.remove("active");
            streamStatus.textContent = "ONLINE";
            streamStatus.className = "status-online";
            URL.revokeObjectURL(audioUrl);
        };

        currentAudio.onerror = () => {
            audioWave.classList.remove("active");
            streamStatus.textContent = "ONLINE";
            streamStatus.className = "status-online";
            URL.revokeObjectURL(audioUrl);
        };

        await currentAudio.play();
        
    } catch (error) {
        console.warn("TTS backend failed, falling back to Browser Speech Synthesis API:", error);
        speakBrowserFallback(text, persona);
    }
}

// Fallback to browser's native SpeechSynthesis API
function speakBrowserFallback(text, persona) {
    if (!window.speechSynthesis) {
        console.error("Browser does not support Speech Synthesis.");
        return;
    }

    window.speechSynthesis.cancel(); // Cancel any current speech

    const utterance = new SpeechSynthesisUtterance(text);

    // Get list of voices
    const voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
        // Try to find a male English voice or any English voice as fallback
        const englishMale = voices.find(v => v.lang.startsWith("en") && v.name.toLowerCase().includes("male"));
        const englishAny = voices.find(v => v.lang.startsWith("en"));
        utterance.voice = englishMale || englishAny || voices[0];
    }

    // Configure voice properties to attempt to mimic commentators
    if (persona === "Ravi Shastri") {
        utterance.rate = 1.15; // High energy
        utterance.pitch = 0.95;
        utterance.volume = 1.0;
    } else if (persona === "Virender Sehwag") {
        utterance.rate = 0.95; // More casual/slower pacing
        utterance.pitch = 0.9;
        utterance.volume = 0.95;
    } else if (persona === "Harbhajan Singh") {
        utterance.rate = 1.0;
        utterance.pitch = 1.1; // Slightly higher pitch
        utterance.volume = 0.95;
    }

    utterance.onstart = () => {
        audioWave.classList.add("active");
        streamStatus.textContent = "ON AIR";
        streamStatus.className = "status-online";
        speakerNameDisplay.textContent = `${persona} (AI Live Radio)`;
    };

    utterance.onend = () => {
        audioWave.classList.remove("active");
        streamStatus.textContent = "ONLINE";
        streamStatus.className = "status-online";
    };

    utterance.onerror = (e) => {
        console.error("SpeechSynthesis error:", e);
        audioWave.classList.remove("active");
        streamStatus.textContent = "ONLINE";
        streamStatus.className = "status-online";
    };

    window.speechSynthesis.speak(utterance);
}

// Event Listeners
simulateBtn.addEventListener("click", () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            action: "simulate",
            persona: currentPersona,
            matchId: matchIdInput.value.trim()
        }));
    }
});

// Persona Button Click Handler
personaButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        personaButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentPersona = btn.getAttribute("data-persona");
        
        // If speaking, restart/speak with new voice style immediately using last commentary text if available
        const lastCommentary = feedContainer.querySelector(".commentary-item .ai-text");
        if (lastCommentary && radioToggle.checked) {
            speakCommentary(lastCommentary.textContent, currentPersona);
        } else {
            speakerNameDisplay.textContent = currentPersona + " Ready";
        }
    });
});

// Radio Live Toggle Change Handler
radioToggle.addEventListener("change", () => {
    if (radioToggle.checked) {
        streamStatus.textContent = "ONLINE";
        streamStatus.className = "status-online";
        speakerNameDisplay.textContent = currentPersona + " Ready";
        
        // Auto-simulate every 10 seconds for realistic live streaming
        autoPlayInterval = setInterval(() => {
            const isSpeaking = (currentAudio && !currentAudio.paused) || (window.speechSynthesis && window.speechSynthesis.speaking);
            if (socket && socket.readyState === WebSocket.OPEN && !isSpeaking) {
                socket.send(JSON.stringify({
                    action: "simulate",
                    persona: currentPersona,
                    matchId: matchIdInput.value.trim()
                }));
            }
        }, 10000);
        
        // Trigger first ball immediately on toggle ON
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                action: "simulate",
                persona: currentPersona,
                matchId: matchIdInput.value.trim()
            }));
        }
    } else {
        streamStatus.textContent = "OFFLINE";
        streamStatus.className = "status-offline";
        speakerNameDisplay.textContent = "None Selected";
        audioWave.classList.remove("active");
        
        // Cancel speech
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        
        // Clear automatic commentary feed interval
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
            autoPlayInterval = null;
        }
    }
});

// Initialize on page load
connectWebSocket();
// Set initial label
speakerNameDisplay.textContent = currentPersona + " Ready";
