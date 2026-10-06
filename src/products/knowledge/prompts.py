SYSTEM_PROMPT = """
You answer employee questions using only the company knowledge context provided.

Rules:
- Use only information contained in the provided context.
- Do not rely on outside knowledge, assumptions, or unstated information.
- If the context does not contain enough information to answer the question, say that the available company knowledge does not provide enough information.
- Do not invent policies, procedures, names, dates, numbers, or business facts.
- If multiple retrieved sources contain conflicting information, clearly state that the sources conflict.
- Answer the employee's question directly and concisely.
- Preserve important names, dates, amounts, software names, and policy details accurately.
- Only cite sources that actually support the answer.
- Return source titles exactly as they appear in the provided context.
"""


def build_knowledge_prompt(
    question: str,
    context_chunks: list[dict],
) -> str:
    formatted_context = []

    for index, chunk in enumerate(context_chunks, start=1):
        formatted_context.append(
            f"""
SOURCE {index}
TITLE: {chunk["title"]}
DOCUMENT ID: {chunk["document_id"]}
CONTENT:
{chunk["content"]}
""".strip()
        )

    context = "\n\n".join(formatted_context)

    return f"""
Answer the employee's question using only the company knowledge below.

COMPANY KNOWLEDGE:
{context}

EMPLOYEE QUESTION:
{question}
""".strip()