from pydantic import BaseModel, Field


class ProcessedDocument(BaseModel):
    document_type: str

    vendor_name: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None

    total_amount: float | None = None
    currency: str | None = None

    purchase_order_number: str | None = None

    line_items: list[str] = Field(default_factory=list)

    notes: str | None = None

    summary: str | None = None


class ValidationIssue(BaseModel):
    field: str | None = None
    message: str


class DocumentValidationResult(BaseModel):
    status: str

    issues: list[ValidationIssue] = Field(default_factory=list)