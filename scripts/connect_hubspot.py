import json

from composio import Composio
from dotenv import load_dotenv
import os

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

# # Print HUBSPOT_CREATE_CONTACT input schema
# tool = composio.tools.get_raw_composio_tool_by_slug(
#     "HUBSPOT_CREATE_CONTACT"
# )

# print("HUBSPOT_CREATE_CONTACT input schema:")
# print(json.dumps(tool.input_parameters, indent=2))

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

