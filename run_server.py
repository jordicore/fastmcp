from fastmcp.server.server import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from fastmcp.tool_loader import generate_openapi_spec_from_supabase, create_client_for_tools
from fastmcp.server.middleware.logging import LoggingMiddleware
import os
import anyio

async def main():
    # --- Authentication Server Setup ---
    print("Generating new RSA key pair for this session...")
    key_pair = RSAKeyPair.generate()
    auth_provider = BearerAuthProvider(public_key=key_pair.public_key)

    # --- Middleware Setup for Better Logging ---
    # This middleware will log requests and responses, including the data payloads,
    # which is extremely useful for debugging tool calls.
    logging_middleware = LoggingMiddleware(
        include_payloads=True,
        max_payload_length=2000  # Log up to 2000 characters of the payload
    )

    # Create the main server that handles authentication and includes the new logging.
    auth_server = FastMCP(
        name="Authenticated Supabase Tool Server",
        instructions="A secure server that provides tools loaded from a Supabase database.",
        stateless_http=True,
        auth=auth_provider,
        middleware=[logging_middleware]  # Add the logging middleware here
    )

    # --- Dynamic Tool Loading ---
    openapi_spec = generate_openapi_spec_from_supabase()
    http_client = create_client_for_tools()
    tools_server = FastMCP.from_openapi(openapi_spec=openapi_spec, client=http_client)

    # --- Mounting ---
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


    # --- Run Server ---
    # Generate a token for client use for this session.
    access_token = key_pair.create_token(audience="my-custom-server", expires_in_seconds=3600) # 1 hour
    print("🚀 Your NEW access token for this session is: 🚀")
    print(access_token)
    print("-" * 80)
    
    # It's better to run the server within the async main function
    await auth_server.run_async(transport="http", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("Server stopped.")
