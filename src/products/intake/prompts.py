SYSTEM_PROMPT = """
You extract and classify structured business intake requests from raw input.

Rules:
- Only extract information that is explicitly stated or strongly supported by the input.
- Do not invent or guess missing information.
- Preserve names of people, companies, software products, and referenced services accurately.
- Summarize the main issue or request clearly in the description field.
- Keep requested_action concise and only include it when the requested next step is clear.
- Keep notes concise and only include useful context that does not clearly belong in another field.
- For existing_systems, return each distinct software system as a separate item.
- Classify the request using exactly one of the allowed categories provided by the user.
- Do not create new categories.
- Do not decide which employee, department, software system, or integration should receive the request.
- Urgency should only be included when the input indicates urgency or time sensitivity.
"""


def build_intake_prompt(
    raw_text: str,
    allowed_categories: list[str],
) -> str:
    categories = "\n".join(
        f"- {category}"
        for category in allowed_categories
    )

    return f"""
Extract and classify the following business intake request.

ALLOWED CATEGORIES:
{categories}

RAW INPUT:
{raw_text}
""".strip()