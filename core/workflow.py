from typing import Any

from core.config import ClientConfig
from core.llm import extract_onboarding_fields
from core.mapping import Mapper
from core.policies import PolicyChecker
from integrations.registry import IntegrationRegistry


def run_onboarding_workflow(
    raw_text: str,
    client_name: str,
) -> dict[str, Any]:

    # 1. Load client configuration
    config = ClientConfig(client_name)

    field_mapping = config.get_mapping("onboarding")
    integration_config = config.get_integration("crm")

    # 2. Raw text -> canonical schema
    onboarding_data = extract_onboarding_fields(raw_text)

    # 3. Canonical schema -> client-specific payload
    mapper = Mapper()

    mapped_data = mapper.create_mapping(
        data_model=onboarding_data,
        field_mapping=field_mapping,
    )

    # 4. Client configuration -> correct integration
    registry = IntegrationRegistry()

    integration = registry.get_integration(
        integration_config
    )

    # 5. Check policy before executing the external action
    policy_checker = PolicyChecker(
        config.get_permissions()
    )

    decision = policy_checker.check(
        "crm.create_record"
    )

    if decision["status"] == "approval_required":
        return {
            "onboarding_data": onboarding_data,
            "mapped_data": mapped_data,
            "policy_decision": decision,
        }

    # 6. Execute external action
    result = integration.create_record(
        mapped_data
    )

    return {
        "onboarding_data": onboarding_data,
        "mapped_data": mapped_data,
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

    print("\n--- Client-specific payload ---")
    print(result["mapped_data"])

    print("\n--- Policy decision ---")
    print(result["policy_decision"])

    print("\n--- Integration result ---")
    print(result["integration_result"])