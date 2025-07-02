from fastmcp.client.client import Client
from fastmcp.client.auth.bearer import BearerAuth
import os

# Get the access token from an environment variable.
# This is more secure and flexible than hardcoding it.
ACCESS_TOKEN = os.environ.get("FASTMCP_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise ValueError("FASTMCP_ACCESS_TOKEN environment variable not set.")

async def main():
    """
    This is an example of how to make an authenticated call to your FastMCP
    server from a client, such as the OpenAI API.
    """
    # Get the URL of your deployed server from the Render dashboard.
    server_url = "https://fastmcp-yroa.onrender.com/mcp"

    # Create a bearer token object.
    token = BearerAuth(token=ACCESS_TOKEN)

    # Create a FastMCP client and provide the token for authentication.
    client = Client(server_url, auth=token)

    # Use the client as an asynchronous context manager.
    async with client:
        # Call the "tools/list" method.
        tools = await client.list_tools()

        print("🎉 Successfully connected and authenticated! 🎉")
        print("Available tools:", [tool.name for tool in tools])


if __name__ == "__main__":
    import anyio
    anyio.run(main)
