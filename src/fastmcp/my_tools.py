
    from fastmcp.tools.tool import tool
    from supabase import create_client
    import os

    # Supabase credentials
    SUPABASE_URL = "https://mqauvofgyzcvdadrohtr.supabase.co"
    SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xYXV2b2ZneXpjdmRhZHJvaHRyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDkzODY4MCwiZXhwIjoyMDY2NTE0NjgwfQ.2xAvZDnCcA890YNCtdKXr3k63DjEnK5uRstVfn0yeZs"

    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    def register_tools():
        # Fetch all enabled tools and their endpoints
        tools_data = supabase.table("mcp_tools").select("*").eq("is_enabled", True).execute().data

        for tool in tools_data:
            tool_id = tool["id"]
            tool_name = tool["tool_name"]
            tool_description = tool["tool_description"]

            # Get endpoint for tool
            endpoint = supabase.table("api_endpoints").select("*").eq("endpoint_id", tool_id).single().execute().data
            if not endpoint:
                continue

            url = endpoint["url"]
            method = endpoint["method"]

            # Get parameters
            params = supabase.table("endpoint_parameters").select("*").eq("endpoint_id", endpoint["id"]).execute().data

            # Build function signature
            param_defs = []
            param_args = []
            for p in params:
                name = p["parameter_name"]
                typ = p["parameter_type"].lower()
                py_type = "str" if typ == "string" else "int" if typ == "integer" else "bool" if typ == "boolean" else "str"
                param_defs.append(f"{name}: {py_type}")
                param_args.append(f'"{name}": {name}')

            param_sig = ", ".join(param_defs)
            body = f'''
@tool(name="{tool_name}", description="{tool_description}")
def {tool_name}({param_sig}) -> str:
    import requests
    payload = {{{", ".join(param_args)}}}
    headers = {{"Content-Type": "application/json"}}
    resp = requests.{method.lower()}("{url}", json=payload, headers=headers)
    return resp.text
'''
            # Register tool dynamically
            exec(body, globals())

    register_tools()
