from integrations.adapters.configurable_mapping import (
    ConfigurableMappingAdapter,
)


def test_build_payload_maps_configured_fields():
    adapter = ConfigurableMappingAdapter(
        {
            "name": "contact_name",
            "email": "contact_email",
        }
    )

    data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
    }

    payload = adapter.build_payload(data)

    assert payload == {
        "contact_name": "Jane Smith",
        "contact_email": "jane@example.com",
    }


def test_build_payload_ignores_unmapped_fields():
    adapter = ConfigurableMappingAdapter(
        {
            "name": "contact_name",
        }
    )

    data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "notes": "Interested in automation",
    }

    payload = adapter.build_payload(data)

    assert payload == {
        "contact_name": "Jane Smith",
    }


def test_build_payload_excludes_none_values():
    adapter = ConfigurableMappingAdapter(
        {
            "name": "contact_name",
            "email": "contact_email",
        }
    )

    data = {
        "name": "Jane Smith",
        "email": None,
    }

    payload = adapter.build_payload(data)

    assert payload == {
        "contact_name": "Jane Smith",
    }


def test_build_payload_preserves_falsey_but_valid_values():
    adapter = ConfigurableMappingAdapter(
        {
            "count": "item_count",
            "enabled": "is_enabled",
            "notes": "notes",
        }
    )

    data = {
        "count": 0,
        "enabled": False,
        "notes": "",
    }

    payload = adapter.build_payload(data)

    assert payload == {
        "item_count": 0,
        "is_enabled": False,
        "notes": "",
    }


def test_build_payload_does_not_modify_source_data():
    adapter = ConfigurableMappingAdapter(
        {
            "name": "contact_name",
        }
    )

    data = {
        "name": "Jane Smith",
    }

    original = data.copy()

    adapter.build_payload(data)

    assert data == original