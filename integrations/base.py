from abc import ABC, abstractmethod
from typing import Any
from core.exceptions import IntegrationError


class BaseIntegration(ABC):
    """
    Contract for external system integrations.

    Product workflows should depend on this interface rather than
    directly depending on HubSpot, Salesforce, Composio, etc.
    """

    @abstractmethod
    def create_record(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a record in the external system.

        Args:
            data:
                Client-specific payload ready to be sent to the
                destination system.

        Returns:
            A dictionary containing the result of the operation.

        Raises:
            IntegrationError:
                If the external operation fails.
        """
        raise NotImplementedError

    def execute_action(
        self,
        action: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a named integration action.

        Integrations that support multiple actions can override
        this method.
        """

        if action == "create_record":
            return self.create_record(data)

        raise IntegrationError(
            f"Unsupported integration action: {action}"
        )