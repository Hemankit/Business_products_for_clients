from typing import Any

from core.config import ClientConfig
from core.policies import PolicyChecker

from src.products.intake.llm import extract_intake_fields
from src.products.intake.router import Router

from integrations.registry import IntegrationRegistry
from integrations.adapters.registry import PayloadAdapterRegistry


def run_intake_workflow(
    raw_text: str,
    client_name: str,
) -> dict[str, Any]:

    # 1. Load client configuration
    config = ClientConfig(client_name)

    routing_rules = config.get_routing()
    allowed_categories = list(routing_rules.keys())

    field_mapping = config.get_mapping("intake")

    # 2. Raw input -> canonical intake request
    intake_request = extract_intake_fields(
        raw_text=raw_text,
        allowed_categories=allowed_categories,
    )

    # 3. Canonical intake request -> routing decision
    router = Router(routing_rules)

    routing_decision = router.route_intake(
        intake_request
    )

    # 4. Resolve the integration selected by routing
    integration_config = config.get_integration(
        routing_decision.integration_name
    )

    # 5. Canonical business data -> integration payload
    canonical_data = intake_request.model_dump(
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

    # 6. Build the selected integration
    integration_registry = IntegrationRegistry()

    client_id = config.get_client_id()
    integration = integration_registry.get_integration(
        config=integration_config,
        client_id=client_id,
    )

    # 7. Check policy before external execution
    policy_checker = PolicyChecker(
        config.get_permissions()
    )

    action = (
        f"{routing_decision.integration_name}."
        "create_record"
    )

    decision = policy_checker.check(action)

    if decision["status"] == "approval_required":
        return {
            "intake_data": intake_request,
            "routing_decision": routing_decision,
            "integration_payload": integration_payload,
            "policy_decision": decision,
        }

    # 8. Execute external action
    result = integration.create_record(
        integration_payload
    )

    return {
        "intake_data": intake_request,
        "routing_decision": routing_decision,
        "integration_payload": integration_payload,
        "policy_decision": decision,
        "integration_result": result,
    }


if __name__ == "__main__":
    raw_text = """
    Hi, my name is James Carter and I work at Acme Solutions.

    We're interested in learning more about your automation services.
    Could someone from sales contact me about the options?

    You can reach me at james@acmesolutions.com.
    """

    result = run_intake_workflow(
        raw_text=raw_text,
        client_name="demo_company",
    )

    print("\n--- Canonical intake request ---")
    print(result["intake_data"])

    print("\n--- Routing decision ---")
    print(result["routing_decision"])

    print("\n--- Integration payload ---")
    print(result["integration_payload"])

    print("\n--- Policy decision ---")
    print(result["policy_decision"])

    if "integration_result" in result:
        print("\n--- Integration result ---")
        print(result["integration_result"])
    else:
        print("\n--- External execution skipped ---")
        print("Approval is required before execution.")