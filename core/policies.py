from typing import Any

from core.exceptions import ClientConfigError


class PolicyChecker:
    def __init__(self, policy: dict[str, Any]):
        self.policy = policy

    def check(self, action: str) -> dict[str, str]:
        action_policy = self.policy.get("actions", {}).get(action)

        if action_policy is None:
            raise ClientConfigError(
                f"No policy configured for action: {action}"
            )

        if action_policy.get("approval", False):
            return {
                "status": "approval_required",
                "action": action,
            }

        return {
            "status": "allowed",
            "action": action,
        }