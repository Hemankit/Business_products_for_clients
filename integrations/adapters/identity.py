from typing import Any

from integrations.adapters.base import BasePayloadAdapter


class IdentityPayloadAdapter(BasePayloadAdapter):

    def build_payload(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        return dict(data)