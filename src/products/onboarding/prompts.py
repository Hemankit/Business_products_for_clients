SYSTEM_PROMPT = """
You extract structured client onboarding information from raw business text.

Rules:
- Only extract information that is explicitly stated or strongly supported by the input.
- Do not invent or guess missing information.
- Preserve names of companies, software products, and services accurately.
- If an optional field is not available, leave it empty.
- For existing_systems, return each distinct software system as a separate item.
- Keep notes concise and only include useful onboarding context that does not clearly belong in another field.
"""


def build_onboarding_prompt(raw_text: str) -> str:
    return f"""
Extract the client onboarding information from the following text.

RAW INPUT:
{raw_text}
""".strip()