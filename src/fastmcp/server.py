from typing import Any

import mcp.server.fastmcp
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


class FastMCP(mcp.server.fastmcp.FastMCP):
    def __init__(self, name: str | None = None, **settings: Any):
        super().__init__(name=name or "FastMCP", **settings)
