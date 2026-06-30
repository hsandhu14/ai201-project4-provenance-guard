import os
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def stylometric_score(text):
    """
    Signal 1: Stylometric heuristics
    Returns a score between 0.0 and 1.0
    Higher score = more AI-like
    """

    words = text.split()

    if len(words) == 0:
        return 0.5

    # Average sentence length
    sentences = re.split(r"[.!?]", text)
    sentences = [s for s in sentences if s.strip()]
    avg_sentence_length = len(words) / max(len(sentences), 1)

    # Vocabulary diversity (type-token ratio)
    diversity = len(set(word.lower() for word in words)) / len(words)

    score = 0.5

    if avg_sentence_length > 22:
        score += 0.2

    if diversity > 0.75:
        score += 0.2

    return min(score, 1.0)


def llm_score(text):
    """
    Signal 2: Groq Llama 3.3 attribution analysis
    Returns a score between 0.0 and 1.0
    Higher score = more AI-like
    """

    prompt = f"""
You are an AI writing attribution assistant.

Analyze the writing below.

Return ONLY a decimal number between 0.0 and 1.0.

0.0 = definitely human
1.0 = definitely AI-generated

Writing:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return float(response.choices[0].message.content.strip())

    except Exception:
        # Return neutral score if API fails
        return 0.5