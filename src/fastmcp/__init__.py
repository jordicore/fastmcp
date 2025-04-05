"""FastMCP - An ergonomic MCP interface."""

from importlib.metadata import version
from fastmcp.server import FastMCP, Context

__version__ = version("fastmcp")
__all__ = [
    "FastMCP",
    "Context",
]
