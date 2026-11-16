from integrations.adapters.base import BasePayloadAdapter
from typing import Any

class ConfigurableMappingAdapter(BasePayloadAdapter):

    def __init__(
        self,
        field_mapping: dict[str, str],
    ):
        self.field_mapping = field_mapping

    def build_payload(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        payload = {}

        for source_field, destination_field in self.field_mapping.items():
            value = data.get(source_field)

            if value is not None:
                payload[destination_field] = value

        return payload