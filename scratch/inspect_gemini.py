import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Waiting 10 seconds to clear rate limits...")
time.sleep(10)

raw_event = "14.3: Shaheen Afridi to Virat Kohli, SIX, what a shot! Over the bowler's head!"
instruction = (
    "You are the legendary cricket commentator Ravi Shastri. Commentate on the raw cricket event. "
    "Speak with extreme energy, drama, and use your iconic catchphrases like 'tracer bullet!', "
    "'like a flash!', 'all the way for six!', 'he's taken that!', 'electrifying atmosphere!', or 'up in the air and gone!' "
    "Keep it punchy, short (1-2 sentences), and highly exciting. Do not output anything else."
)

try:
    print("Calling generate_content...")
    # Create the model with system instruction
    m = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=instruction)
    res = m.generate_content(f"Raw Event: {raw_event}")
    print("Prompt Feedback:", getattr(res, "prompt_feedback", "None"))
    print("Candidates:")
    for idx, c in enumerate(res.candidates):
        part_text = c.content.parts[0].text if c.content and c.content.parts else "No parts"
        print(f"Candidate {idx}: text={repr(part_text)}, finish_reason={c.finish_reason}")
    print("Full response text:", repr(res.text))
except Exception as e:
    print("Error:", e)
