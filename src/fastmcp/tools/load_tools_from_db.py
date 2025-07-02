import os
import asyncpg
from typing import List, Dict, Any


async def get_tools_from_db() -> List[Dict[str, Any]]:
    db_url = os.getenv("SUPABASE_DB_URL")  # e.g., postgres://user:pass@host:5432/dbname
    conn = await asyncpg.connect(dsn=db_url)

    tools_query = """
        SELECT t.tool_name, t.tool_description, e.id as endpoint_id
        FROM mcp_tools t
        JOIN api_endpoints e ON e.endpoint_id = t.id
        WHERE t.is_enabled = true
    """

    param_query = """
        SELECT endpoint_id, parameter_name, parameter_type, is_required, description
        FROM endpoint_parameters
    """

    tools_rows = await conn.fetch(tools_query)
    param_rows = await conn.fetch(param_query)
    await conn.close()

    # Group parameters by endpoint_id
    param_map = {}
    for row in param_rows:
        endpoint_id = str(row["endpoint_id"])
        param_map.setdefault(endpoint_id, []).append(row)

    tools = []
    for row in tools_rows:
        endpoint_id = str(row["endpoint_id"])
        params = param_map.get(endpoint_id, [])

        properties = {
            p["parameter_name"]: {
                "type": p["parameter_type"],
                "description": p["description"],
            }
            for p in params
        }

        required = [p["parameter_name"] for p in params if p["is_required"]]

        tools.append({
            "name": row["tool_name"],
            "description": row["tool_description"],
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        })

    return tools
