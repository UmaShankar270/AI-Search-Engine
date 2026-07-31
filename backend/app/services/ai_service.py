import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

print("API KEY:", os.getenv("GEMINI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")
