from typing import Any

from core.config import ClientConfig
from core.policies import PolicyChecker

from src.products.onboarding.llm import extract_onboarding_fields

from integrations.registry import IntegrationRegistry
from integrations.adapters.registry import PayloadAdapterRegistry


def run_onboarding_workflow(
    raw_text: str,
    client_name: str,
) -> dict[str, Any]:

    # 1. Load client configuration
    config = ClientConfig(client_name)

    field_mapping = config.get_mapping("onboarding")
    integration_config = config.get_integration("crm")

    # 2. Raw text -> canonical onboarding schema
    onboarding_data = extract_onboarding_fields(
        raw_text
    )

    # 3. Canonical onboarding data -> integration payload
    canonical_data = onboarding_data.model_dump(
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

    # 4. Client configuration -> correct integration
    integration_registry = IntegrationRegistry()

    client_id = config.get_client_id()
    integration = integration_registry.get_integration(
        config=integration_config,
        client_id=client_id,
    )

    # 5. Check policy before executing external action
    policy_checker = PolicyChecker(
        config.get_permissions()
    )

    decision = policy_checker.check(
        "crm.create_record"
    )

    if decision["status"] == "approval_required":
        return {
            "onboarding_data": onboarding_data,
            "integration_payload": integration_payload,
            "policy_decision": decision,
        }

    # 6. Execute external action
    result = integration.create_record(
        integration_payload
    )

    return {
        "onboarding_data": onboarding_data,
        "integration_payload": integration_payload,
        "policy_decision": decision,
        "integration_result": result,
    }


if __name__ == "__main__":
    raw_text = """
    Hi, my name is Sarah Johnson and I run operations at Northstar Dental.

    We're looking for help automating our patient onboarding and intake process.
    Right now, new patient information comes in through forms and email, and our
    staff manually moves that information into HubSpot.

    We currently use HubSpot, Google Workspace, and Slack.

    You can reach me at sarah@northstardental.com or 508-555-0147.

    Ideally, we'd like to reduce the amount of manual data entry our front desk
    team has to do and make sure new patient requests get routed to the right person.
    """

    result = run_onboarding_workflow(
        raw_text=raw_text,
        client_name="demo_company",
    )

    print("\n--- Canonical onboarding object ---")
    print(result["onboarding_data"])

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