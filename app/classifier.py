import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client configured for local Ollama
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
model_name = os.getenv("AI_MODEL_NAME", "qwen2.5-coder:7b")

client = OpenAI(
    base_url=base_url,
    api_key="ollama"  # Dummy key required by OpenAI SDK
)

CLASSIFY_SYSTEM_PROMPT = """
You are an AI Triage Specialist for an enterprise support system.

Analyze the user's incoming support request and classify it into an appropriate category and urgency level.

Classification Rules:
1. "category":
   - "Technical": System crashes, API bugs, 500 errors, broken features, login issues, software defects.
   - "Billing": Invoices, payments, refunds, subscription plans, credit card charges.
   - "General": Basic questions, feedback, feature requests, documentation queries, or general inquiries.

2. "urgency":
   - "High": System outages, payment gateway failures, security threats, production down, blocking issues affecting multiple users.
   - "Medium": Specific feature bugs, billing discrepancies, account access issues where workarounds exist.
   - "Low": General questions, minor UI feedback, non-blocking requests.

Return ONLY a valid JSON object with the following exact structure (no markdown formatting, no code blocks):
{
    "category": "Technical" | "Billing" | "General",
    "urgency": "High" | "Medium" | "Low",
    "summary": "Brief 1-sentence summary of the user's issue.",
    "reason": "Short explanation for why this category and urgency were selected."
}
"""


def classify_request(request_text: str) -> dict:
    """
    Analyzes user support request text using local LLM and returns structured JSON classification.
    """
    if not request_text or not request_text.strip():
        return {
            "category": "General",
            "urgency": "Low",
            "summary": "Empty request body.",
            "reason": "No text provided in request."
        }

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
                {"role": "user", "content": f"User Request Text: \"{request_text}\""}
            ],
            temperature=0.1
        )

        raw_output = response.choices[0].message.content.strip()

        # Clean potential markdown JSON backticks if present
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]

        parsed_result = json.loads(raw_output.strip())
        return parsed_result

    except json.JSONDecodeError:
        print("⚠️ Warning: LLM output was not strict JSON. Fallback applied.")
        return {
            "category": "General",
            "urgency": "Medium",
            "summary": "Failed to parse JSON response.",
            "reason": "AI response parsing error."
        }
    except Exception as e:
        print(f"❌ Classification error: {e}")
        return {
            "category": "General",
            "urgency": "Medium",
            "summary": "System error during classification.",
            "reason": str(e)
        }


# Self-testing block with multiple scenarios
if __name__ == "__main__":
    test_cases = [
        "Our payment gateway is down and throwing 500 errors for all customers!",
        "I was charged twice on my credit card for this month's subscription.",
        "Could you please tell me how I can update my profile picture?"
    ]

    print("🧠 Testing AI Request Classifier Module...\n")
    for idx, text in enumerate(test_cases, start=1):
        print(f"--- Test #{idx} ---")
        print(f"Input: \"{text}\"")
        res = classify_request(text)
        print(f"Output: {json.dumps(res, indent=2)}")
        print("-" * 40 + "\n")
