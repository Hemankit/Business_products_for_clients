import voyageai
from dotenv import load_dotenv
from typing import Literal

from core.exceptions import EmbeddingError


load_dotenv()

voyage_client = voyageai.Client()

EMBEDDING_MODEL = "voyage-4-lite"
EMBEDDING_DIMENSION = 1024


def embed_texts(
    texts: list[str],
    input_type: Literal["document", "query"] = "document",
) -> list[list[float]]:
    """
    Generate embeddings for a batch of texts.
    """

    if not texts:
        return []

    try:
        response = voyage_client.embed(
            texts=texts,
            model=EMBEDDING_MODEL,
            input_type=input_type,
            output_dimension=EMBEDDING_DIMENSION,
        )

        return response.embeddings

    except Exception as e:
        raise EmbeddingError(
            f"Failed to generate embeddings: {e}"
        ) from e


def embed_text(
    text: str,
    input_type: Literal["document", "query"] = "document",
) -> list[float]:
    """
    Generate an embedding for a single text.
    """

    embeddings = embed_texts(
        texts=[text],
        input_type=input_type,
    )

    return embeddings[0]
