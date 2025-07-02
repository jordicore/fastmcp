from fastmcp.server.server import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from fastmcp.tool_loader import generate_openapi_spec_from_supabase, create_client_for_tools
import os

# --- Authentication Server Setup ---
# This server's only job is to handle security.
# A new key pair and token will be generated on each server build.
print("Generating new RSA key pair for this session...")
key_pair = RSAKeyPair.generate()
auth_provider = BearerAuthProvider(public_key=key_pair.public_key)

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
    # Generate a token for client use for this session.
    # You will need to get this from the logs after each deployment.
    access_token = key_pair.create_token(audience="my-custom-server", expires_in_seconds=3600) # 1 hour
    print("-" * 80)
    print("🚀 Your NEW access token for this session is: 🚀")
    print(access_token)
    print("-" * 80)
    
    auth_server.run(transport="http", host="0.0.0.0", port=8000)
