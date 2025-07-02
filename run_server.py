from fastmcp.server.server import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from fastmcp.tool_loader import (
    generate_openapi_spec_from_supabase,
    create_client_for_tools,
)
import os

# --- Authentication Server Setup ---
# This server's only job is to handle security.
# By default we generate a new key pair on each boot, but a fixed key can be
# provided via the ``FASTMCP_PRIVATE_KEY`` environment variable.

private_key_env = os.getenv("FASTMCP_PRIVATE_KEY")
public_key_env = os.getenv("FASTMCP_PUBLIC_KEY")

if private_key_env:
    print("Loading RSA key pair from FASTMCP_PRIVATE_KEY environment variable...")
    key_pair = RSAKeyPair.from_private_key(private_key_env)
    public_key = key_pair.public_key
elif public_key_env:
    print("Using public key from FASTMCP_PUBLIC_KEY environment variable...")
    key_pair = None
    public_key = public_key_env
else:
    print("Generating new RSA key pair for this session...")
    key_pair = RSAKeyPair.generate()
    public_key = key_pair.public_key

auth_provider = BearerAuthProvider(public_key=public_key)

# Create the main server that handles authentication.
auth_server = FastMCP(
    name="Authenticated Supabase Tool Server",
    instructions="A secure server that provides tools loaded from a Supabase database.",
    stateless_http=True,
    auth=auth_provider,
)

# --- Dynamic Tool Loading ---
# This section dynamically loads your tools from Supabase.
openapi_spec = generate_openapi_spec_from_supabase()
http_client = create_client_for_tools()
tools_server = FastMCP.from_openapi(openapi_spec=openapi_spec, client=http_client)

# --- Mounting ---
# Mount the server with your tools onto the server that handles authentication.
auth_server.mount(tools_server)


if __name__ == "__main__":
    # Token for client use. Set FASTMCP_ACCESS_TOKEN to supply your own fixed
    # token. Otherwise a new one will be generated (requires a private key).

    access_token = os.getenv("FASTMCP_ACCESS_TOKEN")
    if not access_token:
        if key_pair is None:
            raise RuntimeError(
                "FASTMCP_ACCESS_TOKEN must be set when no private key is available."
            )
        access_token = key_pair.create_token(
            audience=os.getenv("FASTMCP_TOKEN_AUDIENCE", "my-custom-server"),
            expires_in_seconds=int(os.getenv("FASTMCP_TOKEN_EXPIRES_IN", 3600)),
        )

    print("-" * 80)
    print("🚀 Your access token for this session is: 🚀")
    print(access_token)
    print("-" * 80)
    
    auth_server.run(transport="http", host="0.0.0.0", port=8000)
