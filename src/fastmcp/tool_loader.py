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

    # 1. Fetch enabled tools and their corresponding endpoints in a single query.
    response = (
        supabase.table("mcp_tools")
        .select("*, api_endpoints!inner(*)")
        .eq("is_enabled", True)
        .execute()
    )
    
    params_response = supabase.table("endpoint_parameters").select("*").execute()

    if not response.data:
        print("Warning: No enabled tools with linked endpoints found.")
        return {
            "openapi": "3.0.0",
            "info": {"title": "Supabase Dynamic Tools", "version": "1.0.0"},
            "paths": {},
        }
    
    tools_with_endpoints = response.data
    all_params = params_response.data
    
    params_map = {}
    for p in all_params:
        params_map.setdefault(p["endpoint_id"], []).append(p)
        
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Supabase Dynamic Tools", "version": "1.0.0"},
        "paths": {},
    }
    
    json_schema_types = {"string", "number", "integer", "boolean", "array", "object"}

    # 4. Process each tool and add it to the spec
    for item in tools_with_endpoints:
        # The joined 'api_endpoints' field is a LIST. We need the first item.
        endpoints_list = item.get("api_endpoints")
        if not isinstance(endpoints_list, list) or not endpoints_list:
            print(f"  - Skipping tool '{item.get('tool_name')}' (no endpoint data in joined query).")
            continue
            
        endpoint = endpoints_list[0]

        path = urlparse(endpoint["url"]).path
        method = endpoint["method"].lower()
        
        if path not in openapi_spec["paths"]:
            openapi_spec["paths"][path] = {}
            
        path_item = {
            "summary": item["tool_description"],
            "operationId": item["tool_name"],
            "parameters": [],
            "responses": {"200": {"description": "Successful Response"}}
        }
        
        tool_params = params_map.get(endpoint["id"], [])
        body_properties = {}
        body_required_fields = []

        for p in tool_params:
            param_type = str(p.get("parameter_type", "string")).lower()
            if param_type not in json_schema_types:
                param_type = "string"

            if f'{{{p["parameter_name"]}}}' in path:
                path_item["parameters"].append({
                    "name": p["parameter_name"], "in": "path", "required": True,
                    "schema": {"type": param_type}
                })
            elif method == "get":
                path_item["parameters"].append({
                    "name": p["parameter_name"], "in": "query", 
                    "required": p.get("is_required", False), "schema": {"type": param_type}
                })
            else: # POST/PUT/etc.
                body_properties[p["parameter_name"]] = {"type": param_type}
                if p.get("is_required", False):
                    body_required_fields.append(p["parameter_name"])

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
        print(f"  + Added tool '{item['tool_name']}' with path '{path}'")
        
    return openapi_spec

def create_client_for_tools() -> httpx.AsyncClient:
    """
    Creates an httpx.AsyncClient configured to make authenticated requests
    to the tool APIs.
    """
    API_BASE_URL = os.environ.get("TOOL_API_BASE_URL", "https://autocab-api.azure-api.net")
    SUBSCRIPTION_KEY = os.environ.get("OCP_APIM_SUBSCRIPTION_KEY")
    
    if not SUBSCRIPTION_KEY:
        raise ValueError("OCP_APIM_SUBSCRIPTION_KEY environment variable not set.")
        
    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
    }
    
    return httpx.AsyncClient(base_url=API_BASE_URL, headers=headers)
