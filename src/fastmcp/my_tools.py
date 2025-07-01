from fastmcp.tools.tool import tool

@tool
def my_first_tool(name: str) -> str:
    """A simple tool that returns a greeting."""
    return f"Hello, {name}!"

@tool
def my_second_tool(x: int, y: int) -> int:
    """A simple tool that adds two numbers."""
    return x + y
