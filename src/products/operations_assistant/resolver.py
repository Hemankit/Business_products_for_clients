from src.products.operations_assistant.schema import (
    ResolvedOperation,
    OperationRequest,
)
from core.exceptions import ClientConfigError


def resolve_operation(
    operation: OperationRequest,
    operation_config: dict,
) -> ResolvedOperation:

    if operation.action not in operation_config:
        raise ClientConfigError(
            f"Operation '{operation.action}' is not configured."
        )

    config = operation_config[operation.action]

    integration_name = config.get("integration")
    integration_action = config.get("integration_action")

    if not integration_name:
        raise ClientConfigError(
            f"Operation '{operation.action}' "
            "is missing integration configuration."
        )

    if not integration_action:
        raise ClientConfigError(
            f"Operation '{operation.action}' "
            "is missing integration_action configuration."
        )

    return ResolvedOperation(
        business_action=operation.action,
        integration_name=integration_name,
        integration_action=integration_action,
    )