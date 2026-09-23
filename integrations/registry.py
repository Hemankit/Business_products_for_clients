from integrations.base import BaseIntegration
from integrations.mock import MockIntegration


class IntegrationRegistry:

    def get_integration(
        self,
        config: dict,
    ) -> BaseIntegration:

        provider = config.get("provider")

        if provider == "mock":
            return MockIntegration()

        raise ValueError(
            f"Unsupported integration provider: {provider}"
        )