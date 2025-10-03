from fastmcp.server.server import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from fastmcp.tool_loader import generate_openapi_spec_from_supabase, create_client_for_tools
from fastmcp.server.middleware.logging import LoggingMiddleware
import os
import anyio
from cryptography.hazmat.primitives import serialization
from pydantic import SecretStr

async def main():
    # --- Permanent Authentication Key Setup ---
    PRIVATE_KEY_PEM = os.environ.get("FASTMCP_PRIVATE_KEY")
    if not PRIVATE_KEY_PEM:
        raise ValueError(
            "FATAL: FASTMCP_PRIVATE_KEY environment variable not set. "
            "The server cannot start without its permanent private key."
        )

    print("Loading permanent RSA key pair from environment variable 'FASTMCP_PRIVATE_KEY'...")
    
    # Load the private key object from the PEM string
    private_key_obj = serialization.load_pem_private_key(
        PRIVATE_KEY_PEM.encode(),
        password=None
    )

    # Derive the public key object and serialize it to a PEM string
    public_key_obj = private_key_obj.public_key()
    public_key_pem_str = public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    
    # 4. Correctly initialize RSAKeyPair.
    # The private key must be wrapped in pydantic's SecretStr.
    key_pair = RSAKeyPair(
        private_key=SecretStr(PRIVATE_KEY_PEM), 
        public_key=public_key_pem_str
    )
    
    auth_provider = BearerAuthProvider(public_key=key_pair.public_key)

    # --- Middleware Setup for Better Logging ---
    logging_middleware = LoggingMiddleware(include_payloads=True, max_payload_length=2000)

    # --- Main Server Creation ---
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
    access_token = key_pair.create_token(audience="my-custom-server", expires_in_seconds=315360000)
    print("🚀 Your PERMANENT access token is: 🚀")
    print(access_token)
    print("-" * 80)
    
    port_str = os.environ.get("PORT")
    try:
        port = int(port_str) if port_str else 8000
    except ValueError:
        raise ValueError(
            "Invalid PORT environment variable. Expected an integer, "
            f"received: {port_str!r}."
        )

    await auth_server.run_async(transport="http", host="0.0.0.0", port=port)

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("Server stopped.")
