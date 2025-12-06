# ADK MCP Server

A Model Context Protocol (MCP) server built with FastMCP 2.13.3, featuring streamable-HTTP transport and custom routing to `/adkmcp`.

## Features

- **Streamable-HTTP Transport**: Production-ready HTTP transport for remote MCP connections
- **Custom Endpoint**: Accessible at `/adkmcp` instead of the default `/mcp`
- **Time & Timezone Tools**: Get current time, convert between timezones, and list available timezones
- **Resources**: URI-based access to datetime information (e.g., `datetime://America/New_York/now`)
- **Health Monitoring**: Built-in health check and server info endpoints
- **Production Ready**: ASGI-compatible for deployment with Uvicorn

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Development Mode

Run the server directly:

```bash
python adkmcp_server.py
```

The server will start on `http://localhost:8000` with the MCP endpoint at `/adkmcp`.

### Production Mode

Deploy with Uvicorn:

```bash
uvicorn adkmcp_server:create_app --factory --host 0.0.0.0 --port 8000
```

Or with auto-reload for development:

```bash
uvicorn adkmcp_server:create_app --factory --reload --host 127.0.0.1 --port 8000
```

## Available Tools

### 1. `get_current_time`
Get the current time in a specific timezone or UTC.

**Parameters:**
- `timezone_name` (optional): IANA timezone name (e.g., "America/New_York")

**Example:**
```python
get_current_time("America/New_York")
# Returns: "2025-12-05T15:30:45-05:00"
```

### 2. `convert_time`
Convert time from one timezone to another.

**Parameters:**
- `time_str`: Time in ISO 8601 format or 'YYYY-MM-DD HH:MM:SS'
- `from_timezone`: Source IANA timezone name
- `to_timezone`: Target IANA timezone name

**Example:**
```python
convert_time("2025-12-05 15:00:00", "America/New_York", "Europe/London")
# Returns: "2025-12-05T20:00:00+00:00"
```

### 3. `list_timezones`
List available IANA timezone names with optional filtering.

**Parameters:**
- `filter_str` (optional): Filter string (case-insensitive)

**Example:**
```python
list_timezones("America")
# Returns: ["America/New_York", "America/Los_Angeles", ...]
```

### 4. `get_timestamp`
Get the current Unix timestamp.

**Example:**
```python
get_timestamp()
# Returns: 1733432445
```

## Available Resources

### 1. Timezone-specific datetime
**URI Pattern:** `datetime://{timezone}/now`

**Example:**
```
datetime://America/New_York/now
datetime://Europe/London/now
datetime://Asia/Tokyo/now
```

### 2. UTC datetime
**URI:** `datetime://utc/now`

## Custom HTTP Routes

### Health Check
```bash
GET http://localhost:8000/health
# Returns: "OK"
```

### Server Info
```bash
GET http://localhost:8000/info
# Returns JSON with server information
```

## MCP Endpoint

The main MCP endpoint is available at:
```
http://localhost:8000/adkmcp
```

This endpoint supports the Model Context Protocol for:
- Tool execution
- Resource access
- Prompt templates
- Server capabilities discovery

## Testing with MCP Inspector

You can test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/adkmcp
```

## Configuration

The server uses the following default configuration:
- **Host**: 127.0.0.1 (localhost)
- **Port**: 8000
- **Transport**: Streamable-HTTP
- **Endpoint Path**: /adkmcp

You can modify these settings in the `adkmcp_server.py` file or through environment variables in production.

## Architecture

The server is built using:
- **FastMCP 2.13.3**: Framework for building MCP servers
- **Starlette**: ASGI framework for HTTP handling
- **Uvicorn**: ASGI server for production deployment
- **zoneinfo**: Python standard library for timezone handling

## Example Integration

### With Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "adk-mcp": {
      "command": "python",
      "args": ["/path/to/adkmcp_server.py"],
      "transport": "http",
      "url": "http://localhost:8000/adkmcp"
    }
  }
}
```

### With MCP Client

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

# Connect to the server
async with stdio_client() as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize connection
        await session.initialize()

        # Call a tool
        result = await session.call_tool("get_current_time", {
            "timezone_name": "America/New_York"
        })
        print(result)
```

## References

This implementation is inspired by the MCP timeserver example and follows best practices from:
- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol Specification](https://github.com/modelcontextprotocol)
- [Streamable-HTTP Transport Guide](https://blog.cloudflare.com/streamable-http-mcp-servers-python/)

## License

MIT License