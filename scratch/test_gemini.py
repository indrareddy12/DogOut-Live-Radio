import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

try:
    print("Listing models:")
    for m in genai.list_models():
        print(f"Name: {m.name}, Supported Methods: {m.supported_generation_methods}")
except Exception as e:
    print("Error listing models:", e)

try:
    print("Trying generation with gemini-2.5-flash:")
    model = genai.GenerativeModel("gemini-2.5-flash")
    res = model.generate_content("Say hello")
    print("Success 2.5 flash:", res.text)
except Exception as e:
    print("Error 2.5 flash:", e)

try:
    print("Trying generation with gemini-3.5-flash:")
    model = genai.GenerativeModel("gemini-3.5-flash")
    res = model.generate_content("Say hello")
    print("Success 3.5 flash:", res.text)
except Exception as e:
    print("Error 3.5 flash:", e)
