from integrations.base import BaseIntegration
from integrations.mock import MockIntegration
from integrations.composio import ComposioIntegration


class IntegrationRegistry:

    def get_integration(
        self,
        config: dict,
    ) -> BaseIntegration:

        provider = config.get("provider")

        if provider == "mock":
            return MockIntegration()

        if provider == "composio":
            return ComposioIntegration(
                user_id=config.get("user_id"),
                toolkit_slug=config.get("toolkit_slug"),
                action_slug=config.get("action_slug"),
            )

        raise ValueError(
            f"Unsupported integration provider: {provider}"
        )