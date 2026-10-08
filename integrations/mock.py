from typing import Any

from integrations.base import BaseIntegration


class MockIntegration(BaseIntegration):

    def create_record(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "status": "success",
            "data": data,
        }

    def execute_action(
        self,
        action: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "status": "success",
            "action": action,
            "data": data,
        }