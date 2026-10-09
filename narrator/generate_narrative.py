import json
import os
import sys
from pathlib import Path

from google import genai

BASE_DIR = Path(__file__).resolve().parent

FINDINGS_FILE = BASE_DIR / "findings.json"
PROMPT_FILE = BASE_DIR / "prompt.txt"
OUTPUT_FILE = BASE_DIR / "narrative.md"

# Locked generation parameters
MODEL_NAME = "gemini-3.5-flash-lite"
TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 1200


def load_json(path):
    """Load and validate the findings JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path.name}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict) or not data:
        raise ValueError("findings.json must contain a non-empty JSON object.")

    return data


def load_prompt(path):
    """Read the narrative instructions."""
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path.name}")

    prompt = path.read_text(encoding="utf-8").strip()

    if not prompt:
        raise ValueError("prompt.txt is empty.")

    return prompt


def build_offline_narrative(findings):
    """Create a basic narrative without requiring an API."""
    summary = json.dumps(findings, indent=2, ensure_ascii=False)

    return (
        "# Mamaearth Returns & Growth Intelligence\n\n"
        "## Situation\n"
        "The order data was cleaned and analyzed to understand revenue, "
        "returns, customer behavior, and payment-method patterns.\n\n"
        "## Complication\n"
        "Return rates and revenue patterns require attention. "
        "The findings below are the verified analysis data; "
        "no additional numerical claims have been added.\n\n"
        "## Resolution\n"
        "Use the verified findings to prioritize high-return segments, "
        "review the reasons for returns, and monitor revenue trends. "
        "Validate business actions against the underlying data.\n\n"
        "## Verified Findings\n"
        "```json\n"
        f"{summary}\n"
        "```\n\n"
        "## Generation Mode\n"
        "Offline fallback — the AI service was not used."
    )


def generate_with_gemini(prompt, findings, api_key):
    """Generate a narrative using fixed model parameters."""
    client = genai.Client(api_key=api_key)

    request = (
        f"{prompt}\n\n"
        "Use only the verified findings below for numerical claims. "
        "Do not invent facts, metrics, or causal relationships. "
        "Structure the response as Situation, Complication, Resolution, "
        "and a one-line explanation.\n\n"
        "VERIFIED FINDINGS:\n"
        f"{json.dumps(findings, indent=2, ensure_ascii=False)}"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=request,
        config={
            "temperature": TEMPERATURE,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        },
    )

    narrative = getattr(response, "text", None)

    if not narrative or not narrative.strip():
        raise ValueError("The AI service returned an empty narrative.")

    return narrative.strip()


def check_narrative(narrative):
    """Validate the minimum requirements of the generated narrative."""
    if not isinstance(narrative, str) or len(narrative.strip()) < 50:
        raise ValueError("Narrative checker failed: output is too short.")

    required_sections = ["Situation", "Complication", "Resolution"]
    missing = [
        section for section in required_sections
        if section.lower() not in narrative.lower()
    ]

    if missing:
        raise ValueError(
            "Narrative checker failed. Missing sections: "
            + ", ".join(missing)
        )

    return True


def main():
    try:
        findings = load_json(FINDINGS_FILE)
        prompt = load_prompt(PROMPT_FILE)

        api_key = os.getenv("GEMINI_API_KEY")

        if api_key:
            try:
                narrative = generate_with_gemini(
                    prompt, findings, api_key
                )
                mode = "Gemini API"
            except Exception as error:
                print(
                    f"Warning: AI generation failed ({error}). "
                    "Using offline fallback.",
                    file=sys.stderr,
                )
                narrative = build_offline_narrative(findings)
                mode = "Offline fallback"
        else:
            print(
                "GEMINI_API_KEY not set. Using offline fallback.",
                file=sys.stderr,
            )
            narrative = build_offline_narrative(findings)
            mode = "Offline fallback"

        check_narrative(narrative)

        OUTPUT_FILE.write_text(narrative + "\n", encoding="utf-8")

        print(f"Narrative generated successfully ({mode}).")
        print(f"Saved to: {OUTPUT_FILE}")

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
