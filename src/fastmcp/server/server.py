from typing import Any

import mcp.server.fastmcp

from fastmcp.server.context import Context
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


class FastMCP(mcp.server.fastmcp.FastMCP):
    def __init__(self, name: str | None = None, **settings: Any):
        super().__init__(name=name or "FastMCP", **settings)

    def get_context(self) -> Context:
        """
        Returns a Context object. Note that the context will only be valid
        during a request; outside a request, most methods will error.
        """
        try:
            request_context = self._mcp_server.request_context
        except LookupError:
            request_context = None
        return Context(request_context=request_context, fastmcp=self)
