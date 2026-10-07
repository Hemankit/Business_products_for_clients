SYSTEM_PROMPT = """
You extract structured information from business documents.

Rules:
- Only extract information that is explicitly stated or strongly supported by the document.
- Do not invent missing values.
- Preserve vendor names, invoice numbers, purchase order numbers, dates, amounts, and currencies accurately.
- If a field is not present, leave it empty.
- Do not decide whether the document should be approved, rejected, or routed.
- Do not infer whether required fields are valid; deterministic validation happens after extraction.
- For line_items, return each distinct line item as a separate concise entry.
- Keep notes concise and only include useful document context that does not clearly belong in another field.
- Provide a concise summary of the document's purpose and key information.
"""


def build_document_prompt(
    raw_text: str,
    expected_document_type: str,
) -> str:
    return f"""
Extract structured information from the following business document.

EXPECTED DOCUMENT TYPE:
{expected_document_type}

DOCUMENT TEXT:
{raw_text}
""".strip()