import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


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

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        return f"AI Summary Error: {str(e)}"