import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency fallback
    genai = None


# Project root:
# D:\Projects\Gradientts\Project-2\AI-Search-Engine
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Explicitly load backend/.env
ENV_FILE = PROJECT_ROOT / "backend" / ".env"
load_dotenv(ENV_FILE)

api_key = os.getenv("GEMINI_API_KEY")
client = None

if api_key and genai is not None:
    client = genai.Client(api_key=api_key)


def summarize(text: str) -> str:
    """
    Summarize a GitHub README using Gemini AI.
    """

    prompt = f"""
You are an expert software engineer.

Analyze the following GitHub repository README and provide:

1. What this project does.
2. Main technologies used.
3. Key features.
4. Who should use it.

Keep the response under 150 words.
Do NOT copy the README.
Write in professional English.

README:

{text}
"""

    if not api_key:
        return "AI Summary unavailable: GEMINI_API_KEY is not configured."

    if client is None:
        return "AI Summary unavailable: Gemini client could not be initialized."

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        return f"AI Summary Error: {str(e)}"
