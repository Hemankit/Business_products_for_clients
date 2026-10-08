from anthropic import Anthropic
from dotenv import load_dotenv

from core.exceptions import LLMExtractionError
from src.products.onboarding.schemas import OnboardingRequest
from src.products.onboarding.prompts import (
    SYSTEM_PROMPT,
    build_onboarding_prompt,
)

load_dotenv()

client = Anthropic()

MODEL = "claude-sonnet-4-5"


def extract_onboarding_fields(raw_text: str) -> OnboardingRequest:
    response = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_onboarding_prompt(raw_text),
            }
        ],
        output_format=OnboardingRequest,
    )

    if response.stop_reason == "refusal":
        raise LLMExtractionError("The model refused to provide a response.")

    if response.stop_reason == "max_tokens":
        raise LLMExtractionError(
            "Response was truncated; retry with a higher max_tokens."
        )

    if response.parsed_output is None:
        raise LLMExtractionError("No structured onboarding output was returned.")

    return response.parsed_output

if __name__ == "__main__":
    raw_text = """
    Hi, my name is Sarah Johnson and I run operations at Northstar Dental.

    We're looking for help automating our patient onboarding and intake process.
    Right now, new patient information comes in through forms and email, and our
    staff manually moves that information into HubSpot.

    We currently use HubSpot, Google Workspace, and Slack.

    You can reach me at sarah@northstardental.com or 508-555-0147.

    Ideally, we'd like to reduce the amount of manual data entry our front desk
    team has to do and make sure new patient requests get routed to the right person.
    """

    try:
        onboarding_data = extract_onboarding_fields(raw_text)
        print(onboarding_data)
    except LLMExtractionError as e:
        print(f"Error: {e}")