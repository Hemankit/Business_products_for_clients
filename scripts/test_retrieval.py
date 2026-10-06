"""Manual smoke test for the knowledge ingestion/retrieval pipeline.

Ingests a fake document, asks a question about it, and inspects the
`RetrievedChunk` objects returned by `retrieve_knowledge`.

Run with:
    python scripts/test_retrieval.py

Requires a running Postgres (with pgvector) reachable via DATABASE_URL
and a valid VOYAGE_API_KEY in the environment/.env file.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PRODUCTS = REPO_ROOT / "src" / "products"
KNOWLEDGE_DIR = SRC_PRODUCTS / "knowledge"

# These modules use a mix of package-qualified imports (e.g.
# "from knowledge.schemas import ...") and bare imports (e.g.
# "from vector_store import ..."), so all three locations need to be
# importable.
for path in (REPO_ROOT, SRC_PRODUCTS, KNOWLEDGE_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from knowledge.ingestion import ingest_document  # noqa: E402
from knowledge.retriever import retrieve_knowledge  # noqa: E402
from knowledge.schemas import KnowledgeDocument, RetrievedChunk  # noqa: E402
from knowledge.vector_store import delete_document_chunks  # noqa: E402


CLIENT_ID = "test_client"

FAKE_DOCUMENT = KnowledgeDocument(
    document_id="fake-doc-001",
    title="Company Vacation Policy",
    content=(
        "Employees accrue one day of paid vacation for every month "
        "worked, up to a maximum of 20 days per year. Unused vacation "
        "days roll over into the following year, capped at 5 days. "
        "To request time off, employees must submit a request through "
        "the HR portal at least two weeks in advance for approval by "
        "their manager."
    ),
    source="fake-source",
    metadata={"department": "HR", "doc_type": "policy"},
)

QUESTION = "How much paid vacation do employees accrue each month?"


def main() -> None:
    print(f"Ingesting document '{FAKE_DOCUMENT.document_id}' "
          f"for client '{CLIENT_ID}'...")
    result = ingest_document(client_id=CLIENT_ID, document=FAKE_DOCUMENT)
    print("Ingestion result:", result)

    print(f"\nAsking question: {QUESTION!r}")
    chunks = retrieve_knowledge(
        client_id=CLIENT_ID,
        query=QUESTION,
        top_k=3,
    )

    print(f"\nRetrieved {len(chunks)} chunk(s):\n")
    for i, chunk in enumerate(chunks, start=1):
        assert isinstance(chunk, RetrievedChunk)

        print(f"--- Chunk {i} ---")
        print("Type:       ", type(chunk))
        print("document_id:", chunk.document_id)
        print("title:      ", chunk.title)
        print("score:      ", chunk.score)
        print("metadata:   ", chunk.metadata)
        print("content:    ", chunk.content[:200])
        print("as dict:    ", chunk.model_dump())
        print()

    # Clean up the fake document so repeated runs stay idempotent.
    print(f"Cleaning up fake document '{FAKE_DOCUMENT.document_id}'...")
    delete_document_chunks(
        client_id=CLIENT_ID,
        document_id=FAKE_DOCUMENT.document_id,
    )
    print("Done.")


if __name__ == "__main__":
    main()
