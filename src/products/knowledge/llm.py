from anthropic import Anthropic
from dotenv import load_dotenv

from core.exceptions import LLMGenerationError
from knowledge.schemas import RetrievedChunk, KnowledgeAnswer
from knowledge.prompts import SYSTEM_PROMPT, build_knowledge_prompt


load_dotenv()

client = Anthropic()

MODEL = "claude-sonnet-4-5"


def answer_knowledge_question(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> KnowledgeAnswer:

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty")

    if not retrieved_chunks:
        return KnowledgeAnswer(
            answer=(
                "The available company knowledge does not provide "
                "enough information to answer this question."
            ),
            sources=[],
        )

    context_chunks = [
        {
            "document_id": chunk.document_id,
            "title": chunk.title,
            "content": chunk.content,
        }
        for chunk in retrieved_chunks
    ]

    prompt = build_knowledge_prompt(
        question=question,
        context_chunks=context_chunks,
    )

    try:
        response = client.messages.parse(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            output_format=KnowledgeAnswer,
        )

    except Exception as e:
        raise LLMGenerationError(
            f"Failed to generate knowledge answer: {e}"
        ) from e

    if response.stop_reason == "refusal":
        raise LLMGenerationError(
            "The model refused to provide a response."
        )

    if response.stop_reason == "max_tokens":
        raise LLMGenerationError(
            "Response was truncated; retry with a higher max_tokens."
        )

    parsed = response.parsed_output

    if parsed is None:
        raise LLMGenerationError(
            "No structured knowledge answer was returned."
        )

    allowed_titles = {
        chunk.title
        for chunk in retrieved_chunks
    }

    invalid_sources = [
        source
        for source in parsed.sources
        if source not in allowed_titles
    ]

    if invalid_sources:
        raise LLMGenerationError(
            f"Model returned unsupported sources: {invalid_sources}"
        )

    return parsed
