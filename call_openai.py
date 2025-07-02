from fastmcp.client.client import Client, BearerToken

# -----------------------------------------------------------------------------
# IMPORTANT: Replace this with the token printed by your server when it starts.
# -----------------------------------------------------------------------------
ACCESS_TOKEN = "PASTE_YOUR_ACCESS_TOKEN_HERE"


async def main():
    """
    This is an example of how to make an authenticated call to your FastMCP
    server from a client, such as the OpenAI API.
    """
    # Get the URL of your deployed server from the Render dashboard.
    server_url = "https://your-fastmcp-server.onrender.com/mcp"

    # Create a bearer token object.
    token = BearerToken(access_token=ACCESS_TOKEN)

    # Create a FastMCP client and provide the token for authentication.
    client = Client(server_url, auth=token)

    try:
        # Connect to the server.
        await client.connect()

        # Call the "tools/list" method.
        # This will fail if the token is invalid or missing.
        tools = await client.list_tools()

        print("🎉 Successfully connected and authenticated! 🎉")
        print("Available tools:", [tool.name for tool in tools])

    finally:
        # Always disconnect the client when you're done.
        await client.disconnect()


if __name__ == "__main__":
    import anyio
    anyio.run(main)
