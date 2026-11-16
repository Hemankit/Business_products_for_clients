from typing import Any

from core.config import ClientConfig
from core.policies import PolicyChecker

from src.products.document_processing.validator import (
    validate_document,
)
from src.products.document_processing.llm import (
    understand_document,
)

from integrations.registry import IntegrationRegistry
from integrations.adapters.registry import PayloadAdapterRegistry


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

    # 5. Resolve destination configuration
    field_mapping = config.get_mapping(
        "document_processing"
    )

    integration_config = config.get_integration(
        "document_processing"
    )

    # 6. Canonical document -> integration payload
    canonical_data = processed_document.model_dump(
        exclude_none=True
    )

    payload_registry = PayloadAdapterRegistry()

    payload_adapter = payload_registry.get_adapter(
        provider=integration_config["provider"],
        toolkit_slug=integration_config.get(
            "toolkit_slug"
        ),
        action_slug=integration_config.get(
            "action_slug"
        ),
        field_mapping=field_mapping,
    )

    integration_payload = (
        payload_adapter.build_payload(
            canonical_data
        )
    )

    # 7. Check policy before external execution
    policy_checker = PolicyChecker(
        config.get_permissions()
    )

    decision = policy_checker.check(
        "document_processing.create_record"
    )

    if decision["status"] == "approval_required":
        return {
            "document": processed_document,
            "validation": validation_result,
            "integration_payload": integration_payload,
            "policy_decision": decision,
        }

    # 8. Build integration
    integration_registry = IntegrationRegistry()

    client_id = config.get_client_id()
    integration = integration_registry.get_integration(
        config=integration_config,
        client_id=client_id,
    )

    # 9. Execute external action
    result = integration.create_record(
        integration_payload
    )

    return {
        "document": processed_document,
        "validation": validation_result,
        "integration_payload": integration_payload,
        "policy_decision": decision,
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

    if result["validation"].status == "review_required":
        print("\n--- Processing stopped ---")
        print("Document requires review.")

    else:
        print("\n--- Integration payload ---")
        print(result["integration_payload"])

        print("\n--- Policy decision ---")
        print(result["policy_decision"])

        if "integration_result" in result:
            print("\n--- Integration result ---")
            print(result["integration_result"])
        else:
            print("\n--- External execution skipped ---")
            print("Approval is required.")