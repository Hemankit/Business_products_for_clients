from abc import ABC, abstractmethod
from typing import Any


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
            Exception:
                If the external operation fails.
        """
        raise NotImplementedError