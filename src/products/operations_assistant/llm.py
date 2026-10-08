import pydantic
from anthropic import Anthropic
from dotenv import load_dotenv

from core.exceptions import LLMExtractionError
from src.products.operations_assistant.prompts import (
    SYSTEM_PROMPT,
    build_operation_prompt,
)
from src.products.operations_assistant.schema import OperationRequest


load_dotenv()

client = Anthropic()

MODEL = "claude-sonnet-4-5"

# The Anthropic `output_format` (schema-constrained) response mode reliably
# collapses open-ended fields such as `parameters: dict[str, Any]` to `{}`,
# since its constrained decoding grammar has no enumerated keys to anchor on.
# Forced tool-use samples the same JSON schema without that constraint and
# consistently extracts the parameters, so it is used here instead.
EXTRACTION_TOOL_NAME = "extract_operation"

EXTRACTION_TOOL = {
    "name": EXTRACTION_TOOL_NAME,
    "description": "Extract a structured business operation request.",
    "input_schema": OperationRequest.model_json_schema(),
}


def interpret_operation(
    raw_text: str,
    operation_config: dict,
) -> OperationRequest:

    raw_text = raw_text.strip()

    if not raw_text:
        raise ValueError("Raw text cannot be empty.")

    if not operation_config:
        raise ValueError("Operation config cannot be empty.")

    allowed_actions = list(operation_config.keys())

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": build_operation_prompt(
                        raw_text,
                        operation_config,
                    ),
                }
            ],
            tools=[EXTRACTION_TOOL],
            tool_choice={"type": "tool", "name": EXTRACTION_TOOL_NAME},
        )

    except Exception as e:
        raise LLMExtractionError(
            f"Failed to interpret operation: {e}"
        ) from e

    if response.stop_reason == "refusal":
        raise LLMExtractionError(
            "The model refused to provide a response."
        )

    if response.stop_reason == "max_tokens":
        raise LLMExtractionError(
            "Response was truncated; retry with a higher max_tokens."
        )

    tool_use = next(
        (block for block in response.content if block.type == "tool_use"),
        None,
    )

    if tool_use is None:
        raise LLMExtractionError(
            "No structured operation output was returned."
        )

    try:
        parsed = OperationRequest.model_validate(tool_use.input)
    except pydantic.ValidationError as e:
        raise LLMExtractionError(
            f"Model returned an invalid operation request: {e}"
        ) from e

    if parsed.action not in allowed_actions:
        raise LLMExtractionError(
            f"Model returned unsupported operation: {parsed.action}"
        )

    return parsed

if __name__ == "__main__":
    raw_text = """
    Create a follow-up task for Acme Solutions reminding the sales team
    to call them tomorrow about their automation proposal.
    """

    operation_config = {
        "create_follow_up_task": {
            "parameters": {
                "message": {"required": True},
                "due": {"required": True},
            },
        },
        "send_internal_message": {
            "parameters": {
                "message": {"required": True},
                "recipient": {"required": True},
            },
        },
    }

    try:
        operation = interpret_operation(
            raw_text=raw_text,
            operation_config=operation_config,
        )

        print("\n--- Structured operation request ---")
        print(operation)

        print("\n--- Extracted fields ---")
        print(f"Action: {operation.action}")
        print(f"Target: {operation.target}")
        print(f"Parameters: {operation.parameters}")
        print(f"Reason: {operation.reason}")

    except (LLMExtractionError, ValueError) as e:
        print(f"Error interpreting operation: {e}")
 