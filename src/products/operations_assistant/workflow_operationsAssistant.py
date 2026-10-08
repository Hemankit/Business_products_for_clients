from typing import Any

from core.config import ClientConfig
from core.policies import PolicyChecker

from integrations.registry import IntegrationRegistry

from src.products.operations_assistant.llm import interpret_operation
from src.products.operations_assistant.resolver import resolve_operation


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

    # 3. Business operation -> configured integration/action
    resolved_operation = resolve_operation(
        operation=operation_request,
        operation_config=operation_config,
    )

    # 4. Resolve the integration selected by operations.yaml
    integration_config = config.get_integration(
        resolved_operation.integration_name
    )

    registry = IntegrationRegistry()

    integration = registry.get_integration(
        integration_config
    )

    # 5. Check policy before execution
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

    # 6. Build the generic action payload
    action_data = dict(
        operation_request.parameters
    )

    if operation_request.target is not None:
        action_data["target"] = operation_request.target

    # 7. Stop if approval is required
    if decision["status"] == "approval_required":
        return {
            "operation_request": operation_request,
            "resolved_operation": resolved_operation,
            "action_data": action_data,
            "policy_decision": decision,
        }

    # 8. Execute configured integration action
    result = integration.execute_action(
        action=resolved_operation.integration_action,
        data=action_data,
    )

    return {
        "operation_request": operation_request,
        "resolved_operation": resolved_operation,
        "action_data": action_data,
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

    print("\n--- Resolved operation ---")
    print(result["resolved_operation"])

    print("\n--- Action data ---")
    print(result["action_data"])

    print("\n--- Policy decision ---")
    print(result["policy_decision"])

    if "integration_result" in result:
        print("\n--- Integration result ---")
        print(result["integration_result"])
    else:
        print("\n--- Execution skipped ---")
        print("Approval is required.")


  
  
  








    