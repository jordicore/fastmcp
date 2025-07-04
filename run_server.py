from fastmcp.server.server import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from fastmcp.tool_loader import generate_openapi_spec_from_supabase, create_client_for_tools
from fastmcp.server.middleware.logging import LoggingMiddleware
import os
import anyio

async def main():
    # --- Permanent Authentication Key Setup ---
    # Read the permanent private key from the environment variable.
    # This is a critical secret for your server's security.
    PRIVATE_KEY_PEM = os.environ.get("RSA_PRIVATE_KEY_PEM")
    if not PRIVATE_KEY_PEM:
        raise ValueError(
            "FATAL: RSA_PRIVATE_KEY_PEM environment variable not set. "
            "The server cannot start without its permanent private key. "
            "Please ensure this is set in your Render environment variables."
        )

    print("Loading permanent RSA key pair from environment variable...")
    # Initialize RSAKeyPair by passing the private key PEM string to the constructor.
    # The public key is derived automatically.
    key_pair = RSAKeyPair(private_key=PRIVATE_KEY_PEM)
    auth_provider = BearerAuthProvider(public_key=key_pair.public_key)

    # --- Middleware Setup for Better Logging ---
    logging_middleware = LoggingMiddleware(
        include_payloads=True,
        max_payload_length=2000
    )

    # --- Main Server Creation ---
    # Create the server with both permanent auth and enhanced logging.
    auth_server = FastMCP(
        name="Authenticated Supabase Tool Server",
        instructions="A secure server that provides tools loaded from a Supabase database.",
        stateless_http=True,
        auth=auth_provider,
        middleware=[logging_middleware]
    )

    # --- Dynamic Tool Loading & Mounting ---
    openapi_spec = generate_openapi_spec_from_supabase()
    http_client = create_client_for_tools()
    tools_server = FastMCP.from_openapi(openapi_spec=openapi_spec, client=http_client)
    auth_server.mount(tools_server)

    # --- Log Loaded Tools on Startup ---
    print("-" * 80)
    print("✅ Dynamically loaded tools from Supabase:")
    try:
        loaded_tools = await auth_server.get_tools()
        if loaded_tools:
            for tool_name in loaded_tools:
                print(f"  - {tool_name}")
        else:
            print("  - No tools were loaded.")
    except Exception as e:
        print(f"  - Error getting tools: {e}")
    print("-" * 80)

    # --- Server Run ---
    # Generate the permanent token for client use.
    access_token = key_pair.create_token(audience="my-custom-server", expires_in_seconds=315360000) # ~10 years
    print("🚀 Your PERMANENT access token for this session is: 🚀")
    print(access_token)
    print("-" * 80)
    
    await auth_server.run_async(transport="http", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("Server stopped.")
