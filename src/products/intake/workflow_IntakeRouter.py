from typing import Any

from core.config import ClientConfig
from core.policies import PolicyChecker
from core.mapping import Mapper

from src.products.intake.llm import extract_intake_fields
from src.products.intake.router import Router

from integrations.registry import IntegrationRegistry


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

    # 4. Canonical schema -> client-specific payload
    mapper = Mapper()

    mapped_data = mapper.create_mapping(
        data_model=intake_request,
        field_mapping=field_mapping,
    )

    # 5. Routing decision -> correct integration
    integration_config = config.get_integration(
        routing_decision.integration_name
    )

    registry = IntegrationRegistry()

    integration = registry.get_integration(
        integration_config
    )

    # 6. Check policy before external execution
    policy_checker = PolicyChecker(
        config.get_permissions()
    )

    action = (
        f"{routing_decision.integration_name}.create_record"
    )

    decision = policy_checker.check(action)

    if decision["status"] == "approval_required":
        return {
            "intake_data": intake_request,
            "routing_decision": routing_decision,
            "mapped_data": mapped_data,
            "policy_decision": decision,
        }

    # 7. Execute external action
    result = integration.create_record(
        mapped_data
    )

    return {
        "intake_data": intake_request,
        "routing_decision": routing_decision,
        "mapped_data": mapped_data,
        "policy_decision": decision,
        "integration_result": result,
    }


if __name__ == "__main__":
    raw_text = """
    Hi, my name is James Carter and I work at Acme Solutions.

    We noticed that our most recent invoice appears to charge us twice
    for the same service. Could someone please look into this today
    and let us know whether one of the charges can be refunded?

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

    print("\n--- Client-specific payload ---")
    print(result["mapped_data"])

    print("\n--- Policy decision ---")
    print(result["policy_decision"])

    if "integration_result" in result:
        print("\n--- Integration result ---")
        print(result["integration_result"])
    else:
        print("\n--- External execution skipped ---")
        print("Approval is required before execution.")


      
    

    