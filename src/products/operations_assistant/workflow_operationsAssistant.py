from typing import Any

from core.config import ClientConfig
from core.policies import PolicyChecker

from integrations.registry import IntegrationRegistry
from integrations.adapters.registry import PayloadAdapterRegistry

from src.products.operations_assistant.llm import interpret_operation
from src.products.operations_assistant.resolver import resolve_operation
from src.products.operations_assistant.validator import validate_operation


def run_operations_workflow(
    raw_text: str,
    client_name: str,
) -> dict[str, Any]:

    # 1. Load client configuration
    config = ClientConfig(client_name)

    operation_config = config.get_operations()

    # 2. Employee request -> canonical business operation
    operation_request = interpret_operation(
        raw_text=raw_text,
        operation_config=operation_config,
    )

    # 3. Validate required business parameters
    validation_result = validate_operation(
        operation=operation_request,
        operation_config=operation_config,
    )

    # 4. Stop if operation is incomplete
    if validation_result.status == "incomplete":
        return {
            "operation_request": operation_request,
            "validation": validation_result,
        }

    # 5. Business operation -> configured integration/action
    resolved_operation = resolve_operation(
        operation=operation_request,
        operation_config=operation_config,
    )

    # 6. Resolve selected integration configuration
    integration_config = config.get_integration(
        resolved_operation.integration_name
    )

    # 7. Build canonical operation payload
    canonical_payload = dict(
        operation_request.parameters
    )

    if operation_request.target is not None:
        canonical_payload["target"] = (
            operation_request.target
        )

    # 8. Canonical operation payload -> integration payload
    payload_registry = PayloadAdapterRegistry()

    payload_adapter = payload_registry.get_adapter(
        provider=integration_config["provider"],
        toolkit_slug=integration_config.get(
            "toolkit_slug"
        ),
        action_slug=(
            integration_config.get("action_slug")
            or resolved_operation.integration_action
        ),
    )

    integration_payload = (
        payload_adapter.build_payload(
            canonical_payload
        )
    )

    # 9. Check policy before execution
    policy_checker = PolicyChecker(
        config.get_permissions()
    )

    policy_action = (
        f"{resolved_operation.integration_name}."
        f"{resolved_operation.integration_action}"
    )

    decision = policy_checker.check(
        policy_action
    )

    # 10. Stop if approval is required
    if decision["status"] == "approval_required":
        return {
            "operation_request": operation_request,
            "validation": validation_result,
            "resolved_operation": resolved_operation,
            "integration_payload": integration_payload,
            "policy_decision": decision,
        }

    # 11. Build selected integration
    integration_registry = IntegrationRegistry()

    client_id = config.get_client_id()
    integration = integration_registry.get_integration(
        config=integration_config,
        client_id=client_id,
    )

    # 12. Execute configured integration action
    result = integration.execute_action(
        action=resolved_operation.integration_action,
        data=integration_payload,
    )

    return {
        "operation_request": operation_request,
        "validation": validation_result,
        "resolved_operation": resolved_operation,
        "integration_payload": integration_payload,
        "policy_decision": decision,
        "integration_result": result,
    }


if __name__ == "__main__":
    raw_text = """
    Send an internal message to the operations team saying that
    Acme Solutions approved the automation proposal.
    """

    result = run_operations_workflow(
        raw_text=raw_text,
        client_name="demo_company",
    )

    print("\n--- Operation request ---")
    print(result["operation_request"])

    print("\n--- Validation ---")
    print(result["validation"])

    if result["validation"].status == "incomplete":
        print("\n--- Execution stopped ---")
        print("Operation is missing required information.")

        for issue in result["validation"].issues:
            print(f"- {issue.field}: {issue.message}")

    else:
        print("\n--- Resolved operation ---")
        print(result["resolved_operation"])

        print("\n--- Action data ---")
        print(result["integration_payload"])

        print("\n--- Policy decision ---")
        print(result["policy_decision"])

        if "integration_result" in result:
            print("\n--- Integration result ---")
            print(result["integration_result"])
        else:
            print("\n--- Execution skipped ---")
            print("Approval is required.")