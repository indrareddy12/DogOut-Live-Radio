import os
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure GenAI if API key exists
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    has_gemini = True
else:
    has_gemini = False

# Fallback templates in case Gemini is not configured
FALLBACK_PHRASES = {
    "Ravi Shastri": {
        "Dot Ball": [
            "A solid defensive stroke! No run. The bowler asks the question, but the batsman is equal to the task!",
            "Right into the blockhole! Well played, no run. This is turning out to be a fascinating contest!"
        ],
        "Single": [
            "Just a tap and they run! Excellent running between the wickets, just ticking the scoreboard over!",
            "Nudged into the gap for a single. Good, sensible cricket here."
        ],
        "Two Runs": [
            "Good response! Whipped away through the mid-wicket pocket. They will push hard and get two! Great running!"
        ],
        "Boundary Four": [
            "SHOT! That went like a tracer bullet! Absolutely cracked through the covers for four! Exquisite!",
            "Four runs! Edged and past the slip cordon, running away like a flash to the boundary rope!"
        ],
        "Sixer": [
            "HE HAS LAUNCHED THAT! High, handsome, and all the way into the crowd! That is a massive six! Monumental!",
            "All the way for six! A signature blow, straight into the commentary box! The crowd is absolutely electric!"
        ],
        "Wicket (Bowled)": [
            "OUT! CLEAN BOWLED! The off-stump is cartwheeling! Ravi Shastri is screaming, what a delivery!",
            "GONE! He went for the big heave, missed it completely, and the woodwork is shattered! Class bowling!"
        ],
        "Wicket (Caught)": [
            "UP IN THE AIR... AND GONE! Taken comfortably at deep mid-wicket! A massive wicket at a crucial juncture!"
        ],
        "No Ball": [
            "Oh, he has overstepped! That is a NO BALL! Free hit coming up, and this crowd is roaring!"
        ],
        "Wide Ball": [
            "Fired down the leg side, too wide! Extra run to the total. The bowler needs to calm his nerves."
        ]
    },
    "Virender Sehwag": {
        "Dot Ball": [
            "Defended well paaji. But dot balls build pressure. Need to take a single!",
            "Another ball with no run. The bowler is happy, but the batsman is getting his eye in."
        ],
        "Single": [
            "Pushed with soft hands and stole a run. Good, keep rotating the strike.",
            "Got a single paaji. Take it easy, no rush."
        ],
        "Two Runs": [
            "Ran two! The batsman might be tired, but the scoreboard must keep ticking!"
        ],
        "Boundary Four": [
            "Aha! A boundary! Fielders become spectators and spectators become fielders! Cracking hit!",
            "Told the bowler to take it easy, or we'll send it out of the boundary! Four runs!"
        ],
        "Sixer": [
            "BABY! That went out of the stadium! Six runs! The bowler might be remembering the Sultan of Multan!",
            "Sky-high six! Sent the ball straight into orbit! Amazing shot!"
        ],
        "Wicket (Bowled)": [
            "Stumps uprooted paaji! Clean bowled! Tried to use too much brain and the stumps are gone!",
            "Well then, time to head back to the pavilion. The bowler threw the stumps out!"
        ],
        "Wicket (Caught)": [
            "Ball in the air and an easy catch! Account closed, batsman heading back home."
        ],
        "No Ball": [
            "Oh no, foot over the line! No ball! Now the batsman will hit a six on the free hit!"
        ],
        "Wide Ball": [
            "Bowled too wide. Got a run as a gift. Focus on the line, brother."
        ]
    },
    "Harbhajan Singh": {
        "Dot Ball": [
            "No run! Great line and length, kept the batsman completely tied down here.",
            "Dot ball! Brilliant comeback by the bowler. The batsman will have to think a bit."
        ],
        "Single": [
            "Gently pushed off the pads for a single. Good rotational play from the batsmen.",
            "Got a single. Strike change, great game plan."
        ],
        "Two Runs": [
            "Great coordination between the two and completed two runs. Well done boys!"
        ],
        "Boundary Four": [
            "Beautifully timed! Boundary four runs! Pushed into the gap and the ball straight out of the boundary!",
            "What a crack! Four runs here. The sound of the bat was just great!"
        ],
        "Sixer": [
            "HE'S NAILED IT! Balle-balle! This went into the crowd for 6 runs! Great shot!",
            "Boom! That's a massive hit! Clean connection and it sails over the rope for a maximum! Brilliant!"
        ],
        "Wicket (Bowled)": [
            "OUT! Stumps shattered! What a delivery paaji! Great ball, the batsman had no answer!",
            "Clean bowled! Stumps flying everywhere! Absolutely straight ball and the batsman is beaten!"
        ],
        "Wicket (Caught)": [
            "Caught! Ball was in the air but went straight into the fielder's hands. Big wicket!"
        ],
        "No Ball": [
            "No ball! Bowler crossed the line. Free hit coming up! Big chance for the batsman."
        ],
        "Wide Ball": [
            "Wide ball. Bowler lost his direction. One extra run."
        ]
    }
}

class ChatbotService:
    def __init__(self):
        self.model_name = "gemini-1.5-flash"

    def translate_to_persona(self, persona: str, raw_event: str, event_type: str) -> str:
        """
        Translates raw cricket commentary into the voice of a selected commentator.
        """
        if not api_key:
            return self._get_fallback_translation(persona, event_type, raw_event)
            
        system_instructions = {
            "Ravi Shastri": (
                "You are the legendary cricket commentator Ravi Shastri. Commentate on the raw cricket event. "
                "Speak with extreme energy, drama, and use your iconic catchphrases like 'tracer bullet!', "
                "'like a flash!', 'all the way for six!', 'he's taken that!', 'electrifying atmosphere!', or 'up in the air and gone!' "
                "Keep it punchy, short (1-2 sentences), and highly exciting. Do not output anything else."
            ),
            "Virender Sehwag": (
                "You are the witty, casual cricket commentator Virender Sehwag. Commentate on the raw cricket event "
                "in English (with a casual Indian touch). Refer to players as 'paaji', "
                "make bold witty observations, joke around, and keep it extremely light-hearted. Keep it short (1-2 sentences). "
                "Do not output anything else."
            ),
            "Harbhajan Singh": (
                "You are the energetic former cricketer and commentator Harbhajan Singh (Bhajji). Commentate on the "
                "raw cricket event in English (with a passionate Punjabi touch). Focus on spin/bowling dynamics, bat connection, "
                "or batsman attitude. Use phrases like 'that's the way!', 'absolutely cracking!', or 'brilliant shot!' "
                "Keep it passionate and short (1-2 sentences). Do not output anything else."
            )
        }

        instruction = system_instructions.get(persona, system_instructions["Ravi Shastri"])
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=instruction
            )
            response = model.generate_content(
                f"Raw Event: {raw_event}",
                generation_config={"max_output_tokens": 80, "temperature": 0.8}
            )
            return response.text.strip()
        except Exception as e:
            # Fallback to templates on API failure
            return self._get_fallback_translation(persona, event_type, raw_event)

    def _get_fallback_translation(self, persona: str, event_type: str, raw_event: str) -> str:
        persona_phrases = FALLBACK_PHRASES.get(persona, FALLBACK_PHRASES["Ravi Shastri"])
        phrases = persona_phrases.get(event_type, persona_phrases.get("Dot Ball"))
        phrase = random.choice(phrases)
        # Parse names if available
        # Raw event format: "14.3: Shaheen Afridi to Virat Kohli, Tucked away..."
        parts = raw_event.split(",", 1)
        prefix = parts[0] + "! " if len(parts) > 0 else ""
        return f"{prefix}{phrase}"
