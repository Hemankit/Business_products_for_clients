from src.products.document_processing.schema import (
    ProcessedDocument,
    ValidationIssue,
    DocumentValidationResult,
)


def validate_document(
    document: ProcessedDocument,
    rules: dict,
) -> DocumentValidationResult:

    validation_issues = []

    # 1. Validate required fields
    required_fields = rules.get("required_fields", [])

    for field in required_fields:
        value = getattr(document, field, None)

        is_missing = (
            value is None
            or (isinstance(value, str) and not value.strip())
            or (isinstance(value, list) and not value)
        )

        if is_missing:
            validation_issues.append(
                ValidationIssue(
                    field=field,
                    message=f"Missing required field: {field}",
                )
            )

    # 2. Validate purchase order requirement
    if rules.get("require_purchase_order", False):
        if not document.purchase_order_number:
            validation_issues.append(
                ValidationIssue(
                    field="purchase_order_number",
                    message="Purchase order number is required.",
                )
            )

    # 3. Validate positive total
    if rules.get("total_amount_must_be_positive", False):
        if (
            document.total_amount is not None
            and document.total_amount <= 0
        ):
            validation_issues.append(
                ValidationIssue(
                    field="total_amount",
                    message="Total amount must be positive.",
                )
            )

    # 4. Determine processing status
    status = (
        "review_required"
        if validation_issues
        else "valid"
    )

    return DocumentValidationResult(
        status=status,
        issues=validation_issues,
    )