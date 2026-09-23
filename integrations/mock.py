from integrations.base import BaseIntegration
from typing import Any
class MockIntegration(BaseIntegration):
    def create_record(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success", "data": data}