import os
from typing import Any

from composio import Composio

from core.exceptions import IntegrationError
from integrations.base import BaseIntegration


composio_client = Composio(
    api_key=os.getenv("COMPOSIO_API_KEY")
)


class ComposioIntegration(BaseIntegration):

    def __init__(
        self,
        user_id: str,
        toolkit_slug: str,
        action_slug: str,
        composio: Composio = composio_client,
    ):
        self.toolkit_slug = toolkit_slug
        self.action_slug = action_slug

        self.session = composio.sessions.create(
            user_id=user_id,
            tools={
                toolkit_slug: [action_slug],
            },
            sandbox={
                "enable": False,
            },
        )

    def create_record(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        self._require_connection()

        result = self.session.execute(
            self.action_slug,
            arguments=data,
        )

        if result.error:
            raise IntegrationError(
                f"Composio action {self.action_slug} failed: "
                f"{result.error}"
            )

        return {
            "status": "success",
            "data": result.data,
            "metadata": {
                "provider": "composio",
                "action": self.action_slug,
                "log_id": result.log_id,
            },
        }

    def is_connected(self) -> bool:
        toolkits = self.session.toolkits()

        for toolkit in toolkits.items:
            if toolkit.slug != self.toolkit_slug:
                continue

            connection = toolkit.connection

            return bool(
                connection
                and connection.is_active
                and connection.connected_account
            )

        return False

    def _require_connection(self) -> None:
        if not self.is_connected():
         raise IntegrationError(
            "No active Composio connection found for "
            f"toolkit '{self.toolkit_slug}'."
        )

    