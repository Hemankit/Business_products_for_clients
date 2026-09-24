from composio import Composio
from integrations.base import BaseIntegration

from typing import Any
from dotenv import load_dotenv
import os

load_dotenv()

composio_client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

class ComposioIntegration(BaseIntegration):
    def __init__(
        self,
        user_id: str,
        toolkit_slug: str,
        action_slug: str,
        composio: Composio = composio_client,
    ):
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

        result = self.session.execute(
            self.action_slug,
            arguments=data,
        )

        if result.error:
            raise RuntimeError(
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

        
    