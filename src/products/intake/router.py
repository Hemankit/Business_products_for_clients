from typing import Any

from core.exceptions import ClientConfigError
from src.products.intake.schemas import IntakeRequest, RoutingDecision


class Router:
    def __init__(self, routing_config: dict[str, Any]):
        self.config = routing_config

    def route_intake(
        self,
        intake_request: IntakeRequest,
    ) -> RoutingDecision:

        category = intake_request.category

        if category not in self.config:
            raise ClientConfigError(
                f"No routing configuration found for category: {category}"
            )

        route_config = self.config[category]

        if "integration" not in route_config:
            raise ClientConfigError(
                f"Routing configuration for '{category}' is missing integration."
            )

        if "destination" not in route_config:
            raise ClientConfigError(
                f"Routing configuration for '{category}' is missing destination."
            )

        return RoutingDecision(
            category=category,
            integration_name=route_config["integration"],
            destination=route_config["destination"],
            reason=f"Matched routing rule for category: {category}",
        )