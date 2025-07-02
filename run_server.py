from fastmcp.server.server import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
import os

# Generate a key pair for signing and verifying tokens.
# In a real application, you would manage these keys more securely
# (e.g., loading from environment variables or a secret store).
key_pair = RSAKeyPair.generate()

# Create a bearer auth provider with the public key.
# The server will use this to verify incoming tokens.
auth_provider = BearerAuthProvider(public_key=key_pair.public_key)

# Create a long-lived access token to use with the OpenAI API.
# The "audience" should match the server's name or a specific identifier.
# Set expires_in_seconds to a very large number for a semi-permanent token.
ACCESS_TOKEN = key_pair.create_token(audience="my-custom-server", expires_in_seconds=315360000) # ~10 years

# Create an instance of the server, now with authentication.
server = FastMCP(
    name="My Custom Server",
    instructions="A server with my custom tools",
    stateless_http=True,
    auth=auth_provider,
)

@server.tool
def my_first_tool(name: str) -> str:
    """A simple tool that returns a greeting."""
    return f"Hello, {name}!"

@server.tool
def my_second_tool(x: int, y: int) -> int:
    """A simple tool that adds two numbers."""
    return x + y

if __name__ == "__main__":
    # In a real deployment, you would typically provide the private key
    # via an environment variable, not generate it dynamically like this.
    # For this example, we'll print the long-lived token for you to copy.
    print("-" * 80)
    print("🚀 Your long-lived access token for OpenAI API is: 🚀")
    print(ACCESS_TOKEN)
    print("-" * 80)
    server.run(transport="http", host="0.0.0.0", port=8000)
