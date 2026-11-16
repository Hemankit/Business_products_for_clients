import os
import sys

from composio import Composio
from dotenv import load_dotenv

from core.config import ClientConfig

load_dotenv()

composio = Composio(
    api_key=os.getenv("COMPOSIO_API_KEY")
)


def connect_toolkit(
    client_name: str,
    toolkit_slug: str,
) -> None:

    config = ClientConfig(client_name)
    client_id = config.get_client_id()

    session = composio.sessions.create(
        user_id=client_id,
        toolkits=[toolkit_slug],
    )

    connection_request = session.authorize(
        toolkit_slug
    )

    print("\nOpen this URL to connect the account:")
    print(connection_request.redirect_url)

    connected_account = (
        connection_request.wait_for_connection(
            600
        )
    )

    print("\nConnection successful.")
    print(
        f"Connected account: "
        f"{connected_account.id}"
    )


if __name__ == "__main__":
    connect_toolkit(
        client_name=(
            sys.argv[1] if len(sys.argv) > 1 else "demo_company"
        ),
        toolkit_slug=(
            sys.argv[2] if len(sys.argv) > 2 else "hubspot"
        ),
    )