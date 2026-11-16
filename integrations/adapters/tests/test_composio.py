from types import SimpleNamespace

from integrations.composio import ComposioIntegration


class FakeSession:
    def __init__(self):
        self.executed_action = None
        self.executed_arguments = None

    def execute(
        self,
        action_slug,
        arguments,
    ):
        self.executed_action = action_slug
        self.executed_arguments = arguments

        return SimpleNamespace(
            error=None,
            data={"id": "contact_123"},
            log_id="log_123",
        )


class FakeSessions:
    def __init__(self):
        self.session = FakeSession()
        self.create_kwargs = None

    def create(self, **kwargs):
        self.create_kwargs = kwargs
        return self.session


class FakeComposio:
    def __init__(self):
        self.sessions = FakeSessions()


def test_create_record_adapts_payload_before_execution():
    fake_composio = FakeComposio()

    integration = ComposioIntegration(
        user_id="demo_company",
        toolkit_slug="hubspot",
        action_slug="HUBSPOT_CREATE_CONTACT",
        composio=fake_composio,
    )

    payload = {
    "firstname": "Jane",
    "lastname": "Smith",
    "email": "jane@example.com",
    "phone": "555-1234",
    "company": "Acme",
}

    result = integration.create_record(payload)

    session = fake_composio.sessions.session
    assert session.executed_arguments == payload

    result = integration.create_record(
        payload
    )

    session = fake_composio.sessions.session

    assert session.executed_action == (
        "HUBSPOT_CREATE_CONTACT"
    )

    assert session.executed_arguments == {
        "firstname": "Jane",
        "lastname": "Smith",
        "email": "jane@example.com",
        "phone": "555-1234",
        "company": "Acme",
    }

    assert result == {
        "status": "success",
        "data": {
            "id": "contact_123",
        },
        "metadata": {
            "provider": "composio",
            "action": "HUBSPOT_CREATE_CONTACT",
            "log_id": "log_123",
        },
    }

import pytest

from core.exceptions import IntegrationError


class FailingSession:
    def execute(
        self,
        action_slug,
        arguments,
    ):
        return SimpleNamespace(
            error="Provider rejected request",
            data=None,
            log_id="log_failed",
        )


class FailingSessions:
    def create(self, **kwargs):
        return FailingSession()


class FailingComposio:
    def __init__(self):
        self.sessions = FailingSessions()


def test_create_record_raises_integration_error_on_composio_failure():
    integration = ComposioIntegration(
        user_id="demo_company",
        toolkit_slug="hubspot",
        action_slug="HUBSPOT_CREATE_CONTACT",
        composio=FailingComposio(),
    )

    with pytest.raises(
        IntegrationError,
        match="Composio action HUBSPOT_CREATE_CONTACT failed",
    ):
        integration.create_record(
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
            }
        )