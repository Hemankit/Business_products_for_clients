from pydantic import BaseModel, Field
from typing import Any


class OperationRequest(BaseModel):
    action: str

    target: str | None = None

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )

    reason: str | None = None


class OperationResult(BaseModel):
    status: str

    action: str

    result: dict[str, Any] = Field(
        default_factory=dict
    )

class ResolvedOperation(BaseModel):
    business_action: str

    integration_name: str
    integration_action: str