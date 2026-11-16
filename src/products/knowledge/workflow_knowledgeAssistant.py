from typing import Any

from knowledge.llm import answer_knowledge_question
from knowledge.retriever import retrieve_knowledge
from core.config import ClientConfig


def run_knowledge_workflow(
    question: str,
    client_name: str,
    top_k: int = 5,
) -> dict[str, Any]:

    
    config = ClientConfig(client_name)
    client_id = config.get_client_id()

    # 1. Retrieve tenant-scoped company knowledge
    knowledge = retrieve_knowledge(
        client_id=client_id,
        query=question,
        top_k=top_k,
    )

    # 2. Answer using only retrieved company context
    answer = answer_knowledge_question(
        question=question,
        retrieved_chunks=knowledge,
    )

    return {
        "client_id": client_id,
        "question": question,
        "knowledge": knowledge,
        "answer": answer,
    }


if __name__ == "__main__":
    question = (
        "How many vacation days do full-time employees receive?"
    )

    result = run_knowledge_workflow(
        question=question,
        client_name="demo_company",
        top_k=5,
    )

    print("\n--- Client ---")
    print(result["client_id"])

    print("\n--- Question ---")
    print(result["question"])

    print("\n--- Retrieved chunks ---")
    for index, chunk in enumerate(
        result["knowledge"],
        start=1,
    ):
        print(f"\nChunk {index}")
        print(f"Document ID: {chunk.document_id}")
        print(f"Document: {chunk.title}")
        print(f"Score: {chunk.score}")
        print(f"Content: {chunk.content}")

    print("\n--- Knowledge answer ---")
    print(result["answer"].answer)

    print("\n--- Sources ---")
    for source in result["answer"].sources:
        print(f"- {source}")