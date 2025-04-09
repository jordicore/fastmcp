"""FastMCP - An ergonomic MCP interface."""

from importlib.metadata import version
import fastmcp.settings

from fastmcp.server.server import FastMCP
from fastmcp.server.context import Context
from . import clients

__version__ = version("fastmcp")
__all__ = ["FastMCP", "Context", "clients"]
