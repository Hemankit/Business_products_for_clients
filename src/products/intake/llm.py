from anthropic import Anthropic
from src.products.intake.schemas import IntakeRequest
from src.products.intake.prompts import SYSTEM_PROMPT, build_intake_prompt
from core.exceptions import LLMExtractionError
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()
MODEL = "claude-sonnet-4-5"

def extract_intake_fields(raw_text: str, allowed_categories: list[str]) -> IntakeRequest:
  response = client.messages.parse(
    model=MODEL,
    max_tokens=1800,
    system=SYSTEM_PROMPT,
    messages = [
      {
        "role": "user",
        "content": build_intake_prompt(raw_text, allowed_categories)
      }
    ],
    output_format=IntakeRequest
  )
  parsed = response.parsed_output
  if response.stop_reason == "refusal":
    raise LLMExtractionError("The model refused to provide a response.")
  
  if response.stop_reason == "max_tokens":
    raise LLMExtractionError(
              "Response was truncated; retry with a higher max_tokens."
          )
  
  if parsed is None:
    raise LLMExtractionError("No structured intake output was returned.")
  
  
  if parsed.category not in allowed_categories:
    raise LLMExtractionError(
        f"Model returned unsupported category: {parsed.category}"
    )
  return parsed

if __name__ == "__main__":
    raw_text = """
    Hi, my name is James Carter and I work at Acme Solutions.

    We noticed that our most recent invoice appears to charge us twice
    for the same service. Could someone please look into this today
    and let us know whether one of the charges can be refunded?

    You can reach me at james@acmesolutions.com.
    """

    allowed_categories = [
        "sales",
        "support",
        "billing",
        "general",
    ]

    try:
        intake_request = extract_intake_fields(
            raw_text=raw_text,
            allowed_categories=allowed_categories,
        )

        print("\n--- Structured intake request ---")
        print(intake_request)

    except LLMExtractionError as e:
        print(f"Error extracting intake fields: {e}")


  