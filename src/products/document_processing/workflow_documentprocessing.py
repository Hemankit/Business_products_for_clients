from typing import Any

from core.config import ClientConfig
from core.mapping import Mapper

from src.products.document_processing.validator import validate_document
from src.products.document_processing.llm import understand_document
from integrations.registry import IntegrationRegistry 

def run_document_processing_workflow(
    raw_text: str,
    document_type: str,
    client_name: str,
) -> dict[str, Any]:

    # 1. Load client configuration
    config = ClientConfig(client_name)

    rules = config.get_document_processing(
        document_type
    )

    # 2. Raw document -> canonical structured document
    processed_document = understand_document(
        raw_text=raw_text,
        expected_document_type=document_type,
    )

    # 3. Validate against client-specific rules
    validation_result = validate_document(
        document=processed_document,
        rules=rules,
    )

    # 4. Stop if human review is required
    if validation_result.status == "review_required":
        return {
            "document": processed_document,
            "validation": validation_result,
        }

    # 5. Canonical document -> client-specific payload
    field_mapping = config.get_mapping(
        "document_processing"
    )

    mapper = Mapper()

    mapped_document = mapper.create_mapping(
        data_model=processed_document,
        field_mapping=field_mapping,
    )

    # 6. Send mapped document to the appropriate integration if configured
    integration_config = config.get_integration(
        "document_processing"
    )

    registry = IntegrationRegistry()

    integration = registry.get_integration(integration_config)


    result = integration.create_record(
        mapped_document
    )

    return {
        "document": processed_document,
        "validation": validation_result,
        "mapped": mapped_document,
        "integration_result": result,
    }

if __name__ == "__main__":
    review_invoice = """
INVOICE

Vendor: Acme Office Supplies
Invoice Number: INV-4822
Invoice Date: October 3, 2026

Total Amount: $875.00
Currency: USD
"""
    result = run_document_processing_workflow(
        raw_text=review_invoice,
        document_type="invoice",
        client_name="demo_company",
    )

    print("\n--- Processed document ---")
    print(result["document"])

    print("\n--- Validation ---")
    print(result["validation"])

    if "mapped" in result:
        print("\n--- Mapped document ---")
        print(result["mapped"])

        print("\n--- Integration result ---")
        print(result["integration_result"])
    else:
        print("\n--- Processing stopped ---")
        print("Document requires review.")