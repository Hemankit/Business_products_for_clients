from pathlib import Path
from typing import Any

import yaml


class ClientConfig:
    def __init__(
        self,
        client_name: str,
        base_dir: str = "clients",
    ):
        self.client_dir = Path(base_dir) / client_name

        if not self.client_dir.exists():
            raise ValueError(
                f"Client configuration not found: {client_name}"
            )

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        path = self.client_dir / filename

        if not path.exists():
            raise ValueError(
                f"Missing configuration file: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def get_mapping(self, product: str) -> dict[str, str]:
        mappings = self._load_yaml("mappings.yaml")

        mapping = mappings.get(product)

        if mapping is None:
            raise ValueError(
                f"No mapping configured for product: {product}"
            )

        return mapping

    def get_integration(
        self,
        integration_name: str,
    ) -> dict[str, Any]:
        integrations = self._load_yaml("integrations.yaml")

        integration = integrations.get(integration_name)

        if integration is None:
            raise ValueError(
                f"No integration configured: {integration_name}"
            )

        return integration