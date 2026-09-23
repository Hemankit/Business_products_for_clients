
from pydantic import BaseModel, Field


class OnboardingRequest(BaseModel):
    name: str

    email: str | None = None
    phone: str | None = None
    company: str | None = None

    requested_service: str | None = None
    existing_systems: list[str] = Field(default_factory=list)

    notes: str | None = None