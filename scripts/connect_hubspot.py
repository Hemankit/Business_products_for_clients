from composio import Composio
from dotenv import load_dotenv
import os

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

session = composio.sessions.create(
    user_id="demo_company",
    tools={
        "hubspot": ["HUBSPOT_CREATE_CONTACT"],
    },
    sandbox={"enable": False},
)

connection = session.authorize("hubspot")

print(connection.redirect_url)

connected_account = connection.wait_for_connection(timeout=180)

print("Connected:", connected_account.id)