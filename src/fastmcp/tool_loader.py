# src/fastmcp/tool_loader.py
import os
from supabase import create_client
import httpx
from urllib.parse import urlparse

def generate_openapi_spec_from_supabase() -> dict:
    """
    Connects to Supabase using credentials from environment variables,
    fetches tool definitions, and generates a valid OpenAPI specification dictionary.
    """
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")

    print("Connecting to Supabase to fetch tools...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 1. Fetch all necessary data from the database
    tools_response = supabase.table("mcp_tools").select("*").eq("is_enabled", True).execute()
    endpoints_response = supabase.table("api_endpoints").select("*").execute()
    params_response = supabase.table("endpoint_parameters").select("*").execute()

    if not tools_response.data:
        print("Warning: No enabled tools found in 'mcp_tools' table.")
    
    tools = tools_response.data
    endpoints = endpoints_response.data
    all_params = params_response.data

    # 2. Create maps for easier lookup
    endpoint_map = {e["id"]: e for e in endpoints}
    params_map = {}
    for p in all_params:
        params_map.setdefault(p["endpoint_id"], []).append(p)
        
    # 3. Start building the OpenAPI specification
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Supabase Dynamic Tools",
            "version": "1.0.0",
        },
        "paths": {},
    }
    
    json_schema_types = {"string", "number", "integer", "boolean", "array", "object"}

    # 4. Process each tool and add it to the spec
    for tool in tools:
        endpoint = endpoint_map.get(tool.get("endpoint_id"))
        if not endpoint:
            print(f"  - Skipping tool '{tool.get('tool_name')}' (no endpoint found).")
            continue

        # Correctly parse the URL to get just the path
        path = urlparse(endpoint["url"]).path
        method = endpoint["method"].lower()
        
        if path not in openapi_spec["paths"]:
            openapi_spec["paths"][path] = {}
            
        path_item = {
            "summary": tool["tool_description"],
            "operationId": tool["tool_name"],
            "parameters": [],
            "responses": {"200": {"description": "Successful Response"}}
        }
        
        tool_params = params_map.get(endpoint["id"], [])
        body_properties = {}
        body_required_fields = []

        for p in tool_params:
            # Sanitize the parameter type to be a valid JSON schema type
            param_type = str(p.get("parameter_type", "string")).lower()
            if param_type not in json_schema_types:
                print(f"  - Warning: Invalid type '{param_type}' for param '{p['parameter_name']}'. Defaulting to 'string'.")
                param_type = "string"

            # Differentiate between path, query, and body parameters
            if f'{{{p["parameter_name"]}}}' in path:
                # It's a path parameter
                path_item["parameters"].append({
                    "name": p["parameter_name"],
                    "in": "path",
                    "required": True, # Path parameters are always required
                    "schema": {"type": param_type}
                })
            elif method == "get":
                # It's a query parameter for a GET request
                path_item["parameters"].append({
                    "name": p["parameter_name"],
                    "in": "query",
                    "required": p.get("is_required", False),
                    "schema": {"type": param_type}
                })
            else: # POST/PUT/etc.
                # It's a body parameter
                body_properties[p["parameter_name"]] = {"type": param_type}
                if p.get("is_required", False):
                    body_required_fields.append(p["parameter_name"])

        # For POST/PUT, if we found any body parameters, add them to the requestBody
        if body_properties:
            path_item["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": body_properties,
                            "required": body_required_fields
                        }
                    }
                }
            }
        
        openapi_spec["paths"][path][method] = path_item
        print(f"  + Added tool '{tool['tool_name']}' with path '{path}'")
        
    return openapi_spec

def create_client_for_tools() -> httpx.AsyncClient:
    """
    Creates an httpx.AsyncClient that can be used to make requests
    to the tool APIs.
    """
    # NOTE: The base_url here is critical. The paths in your OpenAPI spec will be
    # appended to this URL. You need to set this to the base domain of your tool APIs.
    # For example, if your tool URLs are on Azure, you'd set it here.
    # It's best to manage this via an environment variable.
    
    API_BASE_URL = os.environ.get("TOOL_API_BASE_URL", "https://autocab-api.azure-api.net")
    
    # You can also add authentication headers here if your tool APIs need them.
    # For example: headers={"Authorization": f"Bearer {os.environ.get('TOOL_API_TOKEN')}"}
    return httpx.AsyncClient(base_url=API_BASE_URL)
