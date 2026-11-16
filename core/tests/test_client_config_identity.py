import pytest

from core.config import ClientConfig
from core.exceptions import ClientConfigError


def test_get_client_id_returns_configured_client_id(
    monkeypatch,
):
    config = ClientConfig("demo_company")

    monkeypatch.setattr(
        config,
        "_load_yaml",
        lambda filename: {
            "client_id": "demo_company"
        },
    )

    assert config.get_client_id() == "demo_company"


def test_get_client_id_raises_when_missing(
    monkeypatch,
):
    config = ClientConfig("demo_company")

    monkeypatch.setattr(
        config,
        "_load_yaml",
        lambda filename: {},
    )

    with pytest.raises(
        ClientConfigError,
        match="client.yaml must define client_id",
    ):
        config.get_client_id()


def test_get_client_id_raises_when_blank(
    monkeypatch,
):
    config = ClientConfig("demo_company")

    monkeypatch.setattr(
        config,
        "_load_yaml",
        lambda filename: {
            "client_id": "   "
        },
    )

    with pytest.raises(
        ClientConfigError,
        match="client_id cannot be empty",
    ):
        config.get_client_id()


def test_get_client_id_raises_when_not_string(
    monkeypatch,
):
    config = ClientConfig("demo_company")

    monkeypatch.setattr(
        config,
        "_load_yaml",
        lambda filename: {
            "client_id": 12345
        },
    )

    with pytest.raises(
        ClientConfigError,
        match="client_id must be a string",
    ):
        config.get_client_id()


def test_get_client_id_strips_whitespace(
    monkeypatch,
):
    config = ClientConfig("demo_company")

    monkeypatch.setattr(
        config,
        "_load_yaml",
        lambda filename: {
            "client_id": "  demo_company  "
        },
    )

    assert config.get_client_id() == "demo_company"