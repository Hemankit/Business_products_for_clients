from core.exceptions import ClientConfigError

from src.products.operations_assistant.schema import (
    OperationValidationResult,
    OperationValidationIssue,
    OperationRequest,
)


def validate_operation(
    operation: OperationRequest,
    operation_config: dict,
) -> OperationValidationResult:

    if operation.action not in operation_config:
        raise ClientConfigError(
            f"Operation '{operation.action}' is not configured."
        )

    action_config = operation_config[
        operation.action
    ]

    parameter_config = (
        action_config.get("parameters")
        or {}
    )

    issues = []

    for param_name, param_rules in parameter_config.items():

        if not param_rules.get("required", False):
            continue

        value = operation.parameters.get(param_name)

        is_missing = (
            value is None
            or (
                isinstance(value, str)
                and not value.strip()
            )
        )

        if is_missing:
            issues.append(
                OperationValidationIssue(
                    field=param_name,
                    message=(
                        "Required parameter is missing: "
                        f"{param_name}"
                    ),
                )
            )

    status = (
        "incomplete"
        if issues
        else "valid"
    )

    return OperationValidationResult(
        status=status,
        issues=issues,
    )