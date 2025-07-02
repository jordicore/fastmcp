# src/fastmcp/tool_loader.py
import os
from supabase import create_client, Client
import httpx

def generate_openapi_spec_from_supabase() -> dict:
    """
    Connects to Supabase using credentials from environment variables,
    fetches tool definitions, and generates an OpenAPI specification dictionary.
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

    # 2. Create maps for easier and more efficient lookup
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
    
    # 4. Process each tool and add it to the spec
    for tool in tools:
        endpoint = endpoint_map.get(tool.get("endpoint_id"))
        if not endpoint:
            print(f"  - Skipping tool '{tool.get('tool_name')}' (no endpoint found).")
            continue

        path = endpoint["url"]
        method = endpoint["method"].lower()
        
        if path not in openapi_spec["paths"]:
            openapi_spec["paths"][path] = {}
            
        path_item = {
            "summary": tool["tool_description"],
            "operationId": tool["tool_name"], # This becomes the tool name in FastMCP
            "parameters": [],
            "responses": {
                "200": {"description": "Successful Response"}
            }
        }
        
        tool_params = params_map.get(endpoint["id"], [])
        
        if method == "get":
            for p in tool_params:
                path_item["parameters"].append({
                    "name": p["parameter_name"],
                    "in": "query",
                    "required": p["is_required"],
                    "schema": {"type": p["parameter_type"].lower()}
                })
        elif method in ["post", "put"]:
            properties = {}
            required_fields = []
            for p in tool_params:
                properties[p["parameter_name"]] = {"type": p["parameter_type"].lower()}
                if p["is_required"]:
                    required_fields.append(p["parameter_name"])
            
            path_item["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": properties,
                            "required": required_fields
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
    # For now, we assume all tool APIs are publicly accessible.
    # If they required authentication, you would add it here.
    return httpx.AsyncClient()
