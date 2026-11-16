from typing import Any

from integrations.adapters.base import BasePayloadAdapter


class HubSpotCreateContactAdapter(BasePayloadAdapter):

    def build_payload(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        payload: dict[str, Any] = {}

        email = self._clean_string(
            data.get("email")
        )

        phone = self._clean_string(
            data.get("phone")
        )

        company = self._clean_string(
            data.get("company")
        )

        name = self._clean_string(
            data.get("name")
        )

        if email:
            payload["email"] = email

        if phone:
            payload["phone"] = phone

        if company:
            payload["company"] = company

        if name:
            firstname, lastname = self._split_name(
                name
            )

            payload["firstname"] = firstname

            if lastname:
                payload["lastname"] = lastname

        return payload

    @staticmethod
    def _clean_string(
        value: Any,
    ) -> str | None:

        if not isinstance(value, str):
            return None

        value = value.strip()

        return value or None

    @staticmethod
    def _split_name(
        name: str,
    ) -> tuple[str, str | None]:

        parts = name.split(maxsplit=1)

        firstname = parts[0]

        lastname = (
            parts[1]
            if len(parts) > 1
            else None
        )

        return firstname, lastname