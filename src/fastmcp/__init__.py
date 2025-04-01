"""FastMCP - A more ergonomic interface for MCP servers."""

from importlib.metadata import version
from mcp.server.fastmcp import FastMCP, Context, Image

__version__ = version("fastmcp")
__all__ = ["FastMCP", "Context", "Image"]
