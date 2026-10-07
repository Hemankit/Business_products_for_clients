from pathlib import Path
from typing import Any

import yaml

from core.exceptions import ClientConfigError, IntegrationError, MappingError


class ClientConfig:
    def __init__(
        self,
        client_name: str,
        base_dir: str = "clients",
    ):
        self.client_dir = Path(base_dir) / client_name

        if not self.client_dir.exists():
            raise ClientConfigError(
                f"Client configuration not found: {client_name}"
            )

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        path = self.client_dir / filename

        if not path.exists():
            raise ClientConfigError(
                f"Missing configuration file: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def get_mapping(self, product: str) -> dict[str, str]:
        mappings = self._load_yaml("mappings.yaml")

        mapping = mappings.get(product)

        if mapping is None:
            raise MappingError(
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
            raise IntegrationError(
                f"No integration configured: {integration_name}"
            )

        return integration

    def get_permissions(self) -> dict[str, Any]:
        return self._load_yaml("permissions.yaml")

    def get_routing(self) -> dict[str, Any]:
        return self._load_yaml("routing.yaml")

    def get_document_processing(
    self,
    document_type: str,
) -> dict[str, Any]:
        config = self._load_yaml("document_processing.yaml")

        rules = config.get(document_type)

        if rules is None:
            raise ClientConfigError(
            f"No document processing configuration found "
            f"for document type: {document_type}"
        )

        return rules