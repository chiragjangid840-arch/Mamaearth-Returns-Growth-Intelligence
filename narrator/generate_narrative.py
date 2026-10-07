
import json
import os
from pathlib import Path

from google import genai

BASE_DIR = Path(__file__).resolve().parent

FINDINGS_FILE = BASE_DIR / "findings.json"
PROMPT_FILE = BASE_DIR / "prompt.txt"
OUTPUT_FILE = BASE_DIR / "narrative.md"


def main():
    with open(FINDINGS_FILE, "r", encoding="utf-8") as f:
        findings = json.load(f)

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt = f.read()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    client = genai.Client(api_key=api_key)

    request = f"""
{prompt}

VERIFIED FINDINGS:
{json.dumps(findings, indent=2)}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=request
    )

    narrative = response.text.strip()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(narrative)

    print("Narrative generated successfully!")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
