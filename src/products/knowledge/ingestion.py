from semantic_text_splitter import TextSplitter

from core.exceptions import IngestionError
from knowledge.schemas import KnowledgeDocument
from knowledge.embeddings import embed_texts
from knowledge.vector_store import (
    delete_document_chunks,
    store_chunks,
)


CHUNK_SIZE = 1200

splitter = TextSplitter(CHUNK_SIZE)


def ingest_document(
    client_id: str,
    document: KnowledgeDocument,
) -> dict:

    try:
        # 1. Validate document content
        if not document.content or not document.content.strip():
            raise IngestionError(
                "Document content is empty."
            )

        # 2. Split document into semantic chunks
        chunks = list(
            splitter.chunks(document.content)
        )

        chunks = [
            chunk
            for chunk in chunks
            if chunk.strip()
        ]

        if not chunks:
            raise IngestionError(
                "Document produced no usable chunks."
            )

        # 3. Embed all chunks in one batch
        embeddings = embed_texts(
            texts=chunks,
            input_type="document",
        )

        if len(embeddings) != len(chunks):
            raise IngestionError(
                "Embedding count does not match chunk count."
            )

        # 4. Build storage records
        chunk_records = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            chunk_records.append(
                {
                    "client_id": client_id,
                    "document_id": document.document_id,
                    "title": document.title,
                    "content": chunk,
                    "source": document.source,
                    "chunk_index": index,
                    "metadata": document.metadata,
                    "embedding": embedding,
                }
            )

        # 5. Replace any previously stored version
        delete_document_chunks(
            client_id=client_id,
            document_id=document.document_id,
        )

        # 6. Store new chunks
        store_chunks(chunk_records)

        # 7. Return ingestion summary
        return {
            "status": "success",
            "client_id": client_id,
            "document_id": document.document_id,
            "chunks_stored": len(chunk_records),
        }

    except IngestionError:
        raise

    except Exception as e:
        raise IngestionError(
            f"Failed to ingest document "
            f"{document.document_id}: {e}"
        ) from e

  