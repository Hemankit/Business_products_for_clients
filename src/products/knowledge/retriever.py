from knowledge.schemas import RetrievedChunk
from knowledge.embeddings import embed_text
from vector_store import search_chunks


def retrieve_knowledge(
    client_id: str,
    query: str,
    top_k: int = 5,
) -> list[RetrievedChunk]:

    if not query or not query.strip():
        return []

    query_embedding = embed_text(
        text=query,
        input_type="query",
    )

    return search_chunks(
        client_id=client_id,
        query_embedding=query_embedding,
        top_k=top_k,
    )