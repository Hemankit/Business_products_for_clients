from integrations.base import BaseIntegration
from integrations.mock import MockIntegration
from integrations.composio import ComposioIntegration

from core.exceptions import ProviderError


class IntegrationRegistry:

    def get_integration(
        self,
        config: dict,
        client_id: str,
    ) -> BaseIntegration:

        provider = config.get("provider")

        if provider == "mock":
            return MockIntegration()

        if provider == "composio":
            toolkit_slug = config.get(
                "toolkit_slug"
            )

            action_slug = config.get(
                "action_slug"
            )

            if not toolkit_slug:
                raise ProviderError(
                    "Composio integration requires toolkit_slug."
                )

            if not action_slug:
                raise ProviderError(
                    "Composio integration requires action_slug."
                )

            return ComposioIntegration(
                user_id=client_id,
                toolkit_slug=toolkit_slug,
                action_slug=action_slug,
            )

        raise ProviderError(
            f"Unsupported integration provider: {provider}"
        )