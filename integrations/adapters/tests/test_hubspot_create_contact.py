from integrations.adapters.hubspot_create_contact import (
    HubSpotCreateContactAdapter,
)


def test_build_payload_maps_supported_fields():
    adapter = HubSpotCreateContactAdapter()

    data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "555-1234",
        "company": "Acme",
        "requested_service": "Automation",
    }

    payload = adapter.build_payload(data)

    assert payload == {
        "firstname": "Jane",
        "lastname": "Smith",
        "email": "jane@example.com",
        "phone": "555-1234",
        "company": "Acme",
    }


def test_build_payload_handles_single_name():
    adapter = HubSpotCreateContactAdapter()

    data = {
        "name": "Prince",
        "email": "prince@example.com",
    }

    payload = adapter.build_payload(data)

    assert payload == {
        "firstname": "Prince",
        "email": "prince@example.com",
    }


def test_build_payload_ignores_empty_and_unsupported_fields():
    adapter = HubSpotCreateContactAdapter()

    data = {
        "name": "   ",
        "email": "",
        "phone": None,
        "company": "  Acme Corp  ",
        "requested_service": "Consulting",
        "notes": "Important client",
    }

    payload = adapter.build_payload(data)

    assert payload == {
        "company": "Acme Corp",
    }


def test_build_payload_does_not_modify_source_data():
    adapter = HubSpotCreateContactAdapter()

    data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
    }

    original = data.copy()

    adapter.build_payload(data)

    assert data == original