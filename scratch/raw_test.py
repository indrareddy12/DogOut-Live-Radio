import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")
res = model.generate_content("Say hello and tell me a short joke about cricket.")
print("Res text:", repr(res.text))
