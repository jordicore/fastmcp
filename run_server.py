from fastmcp.server.server import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair

# Generate a key pair for signing and verifying tokens.
# In a real application, you would manage these keys more securely.
key_pair = RSAKeyPair.generate()

# Create a bearer auth provider with the public key.
# The server will use this to verify incoming tokens.
auth_provider = BearerAuthProvider(public_key=key_pair.public_key)

# Create an access token to use with the OpenAI API.
# The "audience" should match the server's name or a specific identifier.
access_token = key_pair.create_token(audience="my-custom-server")


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
    print("-" * 80)
    print("🚀 Your access token for OpenAI API is: 🚀")
    print(access_token)
    print("-" * 80)
    server.run(transport="http", host="0.0.0.0", port=8000)
