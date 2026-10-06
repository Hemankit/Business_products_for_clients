import os
from typing import Any

import psycopg
from dotenv import load_dotenv
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb

from core.exceptions import VectorStoreError
from knowledge.schemas import RetrievedChunk


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def _connect():
    if not DATABASE_URL:
        raise VectorStoreError(
            "DATABASE_URL is not configured."
        )

    conn = psycopg.connect(DATABASE_URL)

    register_vector(conn)

    return conn


def store_chunks(
    chunks: list[dict[str, Any]],
) -> None:

    if not chunks:
        return

    try:
        with _connect() as conn:
            with conn.cursor() as cur:

                for chunk in chunks:
                    cur.execute(
                        """
                        INSERT INTO knowledge_chunks (
                            client_id,
                            document_id,
                            title,
                            content,
                            source,
                            chunk_index,
                            metadata,
                            embedding
                        )
                        VALUES (
                            %s, %s, %s, %s,
                            %s, %s, %s, %s
                        )
                        ON CONFLICT (
                            client_id,
                            document_id,
                            chunk_index
                        )
                        DO UPDATE SET
                            title = EXCLUDED.title,
                            content = EXCLUDED.content,
                            source = EXCLUDED.source,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                        """,
                        (
                            chunk["client_id"],
                            chunk["document_id"],
                            chunk["title"],
                            chunk["content"],
                            chunk.get("source"),
                            chunk["chunk_index"],
                            Jsonb(
                                chunk.get("metadata", {})
                            ),
                            Vector(chunk["embedding"]),
                        ),
                    )

    except VectorStoreError:
        raise

    except Exception as e:
        raise VectorStoreError(
            f"Error storing chunks: {e}"
        ) from e


def search_chunks(
    client_id: str,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[RetrievedChunk]:

    try:
        query_vector = Vector(query_embedding)

        with _connect() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        document_id,
                        title,
                        content,
                        metadata,
                        1 - (embedding <=> %s) AS score
                    FROM knowledge_chunks
                    WHERE client_id = %s
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (
                        query_vector,
                        client_id,
                        query_vector,
                        top_k,
                    ),
                )

                rows = cur.fetchall()

        return [
            RetrievedChunk(
                document_id=row[0],
                title=row[1],
                content=row[2],
                metadata=row[3],
                score=float(row[4]),
            )
            for row in rows
        ]

    except VectorStoreError:
        raise

    except Exception as e:
        raise VectorStoreError(
            f"Error searching chunks: {e}"
        ) from e

def delete_document_chunks(
    client_id: str,
    document_id: str,
) -> None:
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM knowledge_chunks
                    WHERE client_id = %s
                    AND document_id = %s
                    """,
                    (
                        client_id,
                        document_id,
                    ),
                )

    except VectorStoreError:
        raise

    except Exception as e:
        raise VectorStoreError(
            f"Error deleting chunks: {e}"
        ) from e