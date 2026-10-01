from pydantic import BaseModel, Field


class IntakeRequest(BaseModel):
    name: str | None = None

    email: str | None = None
    phone: str | None = None
    company: str | None = None

    category: str

    subject: str | None = None
    description: str

    requested_action: str | None = None

    existing_systems: list[str] = Field(default_factory=list)

    urgency: str | None = None

    notes: str | None = None


class RoutingDecision(BaseModel):
    category: str

    integration_name: str
    destination: str

    reason: str | None = None