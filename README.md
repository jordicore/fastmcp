<!-- omit in toc -->
# FastMCP 🚀

<div align="center">

[![PyPI - Version](https://img.shields.io/pypi/v/fastmcp.svg)](https://pypi.org/project/fastmcp)
[![Tests](https://github.com/jlowin/fastmcp/actions/workflows/run-tests.yml/badge.svg)](https://github.com/jlowin/fastmcp/actions/workflows/run-tests.yml)
[![License](https://img.shields.io/github/license/jlowin/fastmcp.svg)](https://github.com/jlowin/fastmcp/blob/main/LICENSE)

A fast, Pythonic way to build Model Context Protocol servers

</div>

Want to connect your LLMs to data and tools? FastMCP makes it simple! 

In just a few lines of code, you can expose your functionality through a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server:

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

That's it! FastMCP handles all the complex protocol details and server management, so you can focus on building great tools. It's designed to be high-level and Pythonic - in most cases, decorating a function is all you need.

🚨 🚧 🏗️ *FastMCP is under active development, as is the MCP specification itself. Core features are working but some advanced capabilities are still in progress.* 

Key features:
* **Fast**: High-level interface means less code and faster development
* **Simple**: Build MCP servers with minimal boilerplate
* **Pythonic**: Feels natural to Python developers
* **Complete***: FastMCP aims to provide a full implementation of the core MCP specification

(\*emphasis on *aims* during construction)

<!-- omit in toc -->
## Table of Contents

- [Installation](#installation)
- [Quickstart](#quickstart)
- [What is MCP?](#what-is-mcp)
- [Core Concepts](#core-concepts)
  - [Server](#server)
  - [Resources](#resources)
  - [Tools](#tools)
  - [Prompts](#prompts)
  - [Images](#images)
  - [Context](#context)
- [Deployment](#deployment)
  - [Development](#development)
  - [Claude Desktop](#claude-desktop)
- [Examples](#examples)
  - [Echo Server](#echo-server)
  - [SQLite Explorer](#sqlite-explorer)

## Installation

```bash
# We strongly recommend installing with uv
brew install uv  # on macOS
uv pip install fastmcp
```

Or with pip:
```bash
pip install fastmcp
```

## Quickstart

Let's create a simple MCP server that exposes a calculator tool and some data:

```python
from fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
```

To use this server, you have two options:

1. Install it in [Claude Desktop](https://claude.ai/download):
```bash
fastmcp install server.py
```

2. Test it with the MCP Inspector:
```bash
fastmcp dev server.py
```

![MCP Inspector](docs/images/mcp-inspector.png)

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. Think of it like a web API, but specifically designed for LLM interactions. MCP servers can:

- Expose data through **Resources** (like GET endpoints)
- Provide functionality through **Tools** (like POST endpoints)
- Define interaction patterns through **Prompts** (reusable templates for LLM interactions)

## Core Concepts

*Note: All code examples below assume you've created a FastMCP server instance called `mcp`.*

### Server

The FastMCP server is your core interface to the MCP protocol. It handles connection management, protocol compliance, and message routing:

```python
from fastmcp import FastMCP

# Create a named server
mcp = FastMCP("My App")

# Configure host/port for HTTP transport (optional)
mcp = FastMCP("My App", host="localhost", port=8000)
```

### Resources

Resources are how you expose data to LLMs. They're similar to GET endpoints in a REST API - they provide data but shouldn't perform significant computation or have side effects. Some examples:

- File contents
- Database schemas
- API responses
- System information

Resources can be static:
```python
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"
```

Or dynamic with parameters (FastMCP automatically handles these as MCP templates):
```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Dynamic user data"""
    return f"Profile data for user {user_id}"
```

### Tools

Tools let LLMs take actions through your server. Unlike resources, tools are expected to perform computation and have side effects. They're similar to POST endpoints in a REST API.

Simple calculation example:
```python
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m ** 2)
```

HTTP request example:
```python
import httpx

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/{city}"
        )
        return response.text
```

### Prompts

Prompts are reusable templates that help LLMs interact with your server effectively. They're like "best practices" encoded into your server. A prompt can be as simple as a string:

```python
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
```

Or a more structured sequence of messages:
```python
from fastmcp.prompts.base import UserMessage, AssistantMessage

@mcp.prompt()
def debug_error(error: str) -> list[Message]:
    return [
        UserMessage("I'm seeing this error:"),
        UserMessage(error),
        AssistantMessage("I'll help debug that. What have you tried so far?")
    ]
```


### Images

FastMCP provides an `Image` class that automatically handles image data in your server:

```python
from fastmcp import FastMCP, Image
from PIL import Image as PILImage

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    
    # FastMCP automatically handles conversion and MIME types
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def load_image(path: str) -> Image:
    """Load an image from disk"""
    # FastMCP handles reading and format detection
    return Image(path=path)
```

Images can be used as the result of both tools and resources.

### Context

The Context object gives your tools and resources access to MCP capabilities. To use it, add a parameter annotated with `fastmcp.Context`:

```python
from fastmcp import FastMCP, Context

@mcp.tool()
async def long_task(files: list[str], ctx: Context) -> str:
    """Process multiple files with progress tracking"""
    for i, file in enumerate(files):
        ctx.info(f"Processing {file}")
        await ctx.report_progress(i, len(files))
        
        # Read another resource if needed
        data = await ctx.read_resource(f"file://{file}")
        
    return "Processing complete"
```

The Context object provides:
- Progress reporting through `report_progress()`
- Logging via `debug()`, `info()`, `warning()`, and `error()`
- Resource access through `read_resource()`
- Request metadata via `request_id` and `client_id`

## Deployment

The FastMCP CLI helps you develop and deploy MCP servers.

Note that for all deployment commands, you are expected to provide the fully qualified path to your server object. For example, if you have a file `server.py` that contains a FastMCP server named `my_server`, you would provide `path/to/server.py:my_server`.

If your server variable has one of the standard names (`mcp`, `server`, or `app`), you can omit the server name from the path and just provide the file: `path/to/server.py`.

### Development

Test and debug your server with the MCP Inspector:
```bash
# Provide the fully qualified path to your server
fastmcp dev server.py:my_mcp_server

# Or just the file if your server is named 'mcp', 'server', or 'app'
fastmcp dev server.py
```

Your server is run in an isolated environment, so you'll need to indicate any dependencies with the `--with` flag. FastMCP is automatically included. If you are working on a uv project, you can use the `--with-editable` flag to mount your current directory:   

```bash
# With additional packages
fastmcp dev server.py --with pandas --with numpy

# Using your project's dependencies and up-to-date code
fastmcp dev server.py --with-editable .
```

### Claude Desktop

Install your server in Claude Desktop:
```bash
# Basic usage (name is taken from your FastMCP instance)
fastmcp install server.py

# With a custom name
fastmcp install server.py --name "My Server"

# With dependencies
fastmcp install server.py --with pandas --with numpy

# Replace an existing server
fastmcp install server.py --force
```

The server name in Claude will be:
1. The `--name` parameter if provided
2. The `name` from your FastMCP instance
3. The filename if the server can't be imported

## Examples

### Echo Server
A simple server demonstrating resources, tools, and prompts:

```python
from fastmcp import FastMCP

mcp = FastMCP("Echo")

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"

@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"
```

### SQLite Explorer
A more complex example showing database integration:

```python
from fastmcp import FastMCP
import sqlite3

mcp = FastMCP("SQLite Explorer")

@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource"""
    conn = sqlite3.connect("database.db")
    schema = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return "\n".join(sql[0] for sql in schema if sql[0])

@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely"""
    conn = sqlite3.connect("database.db")
    try:
        result = conn.execute(sql).fetchall()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.prompt()
def analyze_table(table: str) -> str:
    """Create a prompt template for analyzing tables"""
    return f"""Please analyze this database table:
Table: {table}
Schema: 
{get_schema()}

What insights can you provide about the structure and relationships?"""
```