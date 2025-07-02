from fastmcp.server.server import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from fastmcp.tool_loader import generate_openapi_spec_from_supabase, create_client_for_tools
import os

# --- Authentication Server Setup ---
# This server's only job is to handle security.
# It will require a valid bearer token for any request.

# First, get the private key from Render's environment variables to keep it secure.
PRIVATE_KEY_PEM = os.environ.get("RSA_PRIVATE_KEY_PEM")
if not PRIVATE_KEY_PEM:
    # On the first run after setting the env var, Render might still be starting.
    # We will generate a temporary key to avoid crashing, but the real key
    # from the environment will be used on subsequent runs.
    print("Warning: RSA_PRIVATE_KEY_PEM not found. Generating a temporary key.")
    PRIVATE_KEY_PEM = RSAKeyPair.generate().private_key

# Initialize RSAKeyPair with the provided private key
key_pair = RSAKeyPair.from_private_key(PRIVATE_KEY_PEM)
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

# 1. Generate the OpenAPI specification from your database.
openapi_spec = generate_openapi_spec_from_supabase()

# 2. Create an HTTP client that FastMCP will use to call your tool APIs.
http_client = create_client_for_tools()

# 3. Create a new FastMCP instance from the OpenAPI spec.
# This instance contains all your tools from the database.
tools_server = FastMCP.from_openapi(openapi_spec=openapi_spec, client=http_client)

# --- Mounting ---
# Now, we mount the server containing your tools onto the server that handles auth.
# This means any request to the main server will first be checked for a valid
# token, and then, if authenticated, it will have access to all the tools.
auth_server.mount(tools_server)


if __name__ == "__main__":
    # Generate a token for client use. This token will be permanent
    # as long as the RSA_PRIVATE_KEY_PEM environment variable is set.
    ACCESS_TOKEN = key_pair.create_token(audience="my-custom-server", expires_in_seconds=315360000) # ~10 years
    print("-" * 80)
    print("🚀 Your permanent access token for OpenAI API is: 🚀")
    print(ACCESS_TOKEN)
    print("-" * 80)
    
    auth_server.run(transport="http", host="0.0.0.0", port=8000)
