from abc import ABC, abstractmethod
from typing import Any


class BasePayloadAdapter(ABC):

    @abstractmethod
    def build_payload(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert canonical/business data into the exact payload
        expected by a specific provider action.
        """
        raise NotImplementedError