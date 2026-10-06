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
from knowledge.schemas import KnowledgeDocument  # noqa: E402


if __name__ == "__main__":
    document = KnowledgeDocument(
        document_id="employee_handbook",
        title="Employee Handbook",
        content="""
        Full-time employees receive 15 paid vacation days per year.

        Employees should request planned vacation at least two weeks
        in advance through their manager.

        Unused vacation days do not roll over into the following year.
        """,
        source="manual_test",
        metadata={
            "department": "hr",
        },
    )

    result = ingest_document(
        client_id="demo_company",
        document=document,
    )

    print(result)