import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

raw_event = "14.3: Shaheen Afridi to Virat Kohli, SIX, what a shot! Over the bowler's head!"
instruction = (
    "You are the legendary cricket commentator Ravi Shastri. Commentate on the raw cricket event. "
    "Speak with extreme energy, drama, and use your iconic catchphrases like 'tracer bullet!', "
    "'like a flash!', 'all the way for six!', 'he's taken that!', 'electrifying atmosphere!', or 'up in the air and gone!' "
    "Keep it punchy, short (1-2 sentences), and highly exciting. Do not output anything else."
)

m = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=instruction)

print("Without generation_config:")
res = m.generate_content(f"Raw Event: {raw_event}")
print(repr(res.text))

print("\nWith generation_config (max_output_tokens=80, temperature=0.8):")
res2 = m.generate_content(f"Raw Event: {raw_event}", generation_config={"max_output_tokens": 80, "temperature": 0.8})
print(repr(res2.text))
