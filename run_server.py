from fastmcp.server.server import FastMCP

# Create an instance of the server and add the tools.
server = FastMCP(
    name="My Custom Server",
    instructions="A server with my custom tools",
)

@server.tool
def my_first_tool(name: str) -> str:
    """A simple tool that returns a greeting."""
    return f"Hello, {name}!"

@server.tool
def my_second_tool(x: int, y: int) -> int:
    """A simple tool that adds two numbers."""
    return x + y

if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)
