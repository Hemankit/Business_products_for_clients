from integrations.adapters.base import BasePayloadAdapter
from integrations.adapters.configurable_mapping import (
    ConfigurableMappingAdapter,
)
from integrations.adapters.hubspot_create_contact import (
    HubSpotCreateContactAdapter,
)
from integrations.adapters.identity import IdentityPayloadAdapter

class PayloadAdapterRegistry:

    def __init__(self):
        self._adapters = {
            (
                "composio",
                "hubspot",
                "HUBSPOT_CREATE_CONTACT",
            ): HubSpotCreateContactAdapter,
        }

    def get_adapter(
        self,
        provider: str,
        toolkit_slug: str | None = None,
        action_slug: str | None = None,
        field_mapping: dict[str, str] | None = None,
    ) -> BasePayloadAdapter:

        key = (
            provider,
            toolkit_slug,
            action_slug,
        )

        adapter_class = self._adapters.get(key)

        if adapter_class is not None:
            return adapter_class()

        if field_mapping is not None:
            return ConfigurableMappingAdapter(
                field_mapping=field_mapping
            )
        if provider == "mock":
            return IdentityPayloadAdapter()

        raise ValueError(
            "No payload adapter registered and no field mapping "
            "was provided for "
            f"provider={provider}, "
            f"toolkit={toolkit_slug}, "
            f"action={action_slug}"
        )