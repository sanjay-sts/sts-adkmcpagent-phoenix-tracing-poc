"""
ADK MCP Server using FastMCP with Streamable-HTTP Transport

This MCP server demonstrates:
- FastMCP 2.13.3 implementation
- Streamable-HTTP transport for production deployments
- Custom routing to /adkmcp endpoint
- Example tools and resources similar to timeserver patterns
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, available_timezones
from typing import Optional
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Initialize FastMCP server
mcp = FastMCP("ADK-MCP-Server")


# Tools
@mcp.tool()
def get_current_time(timezone_name: Optional[str] = None) -> str:
    """
    Get the current time in a specific timezone or UTC.

    Args:
        timezone_name: IANA timezone name (e.g., 'America/New_York', 'Europe/London').
                      If not provided, returns UTC time.

    Returns:
        Current time as ISO 8601 formatted string

    Example:
        get_current_time("America/New_York") -> "2025-12-05T15:30:45-05:00"
    """
    try:
        if timezone_name:
            if timezone_name not in available_timezones():
                return f"Error: Invalid timezone '{timezone_name}'. Use list_timezones to see available options."
            tz = ZoneInfo(timezone_name)
            current_time = datetime.now(tz)
        else:
            current_time = datetime.now(timezone.utc)

        return current_time.isoformat()
    except Exception as e:
        return f"Error getting time: {str(e)}"


@mcp.tool()
def convert_time(
    time_str: str,
    from_timezone: str,
    to_timezone: str
) -> str:
    """
    Convert time from one timezone to another.

    Args:
        time_str: Time in ISO 8601 format or 'YYYY-MM-DD HH:MM:SS'
        from_timezone: Source IANA timezone name
        to_timezone: Target IANA timezone name

    Returns:
        Converted time as ISO 8601 formatted string

    Example:
        convert_time("2025-12-05 15:00:00", "America/New_York", "Europe/London")
    """
    try:
        # Validate timezones
        if from_timezone not in available_timezones():
            return f"Error: Invalid source timezone '{from_timezone}'"
        if to_timezone not in available_timezones():
            return f"Error: Invalid target timezone '{to_timezone}'"

        # Parse the time string
        try:
            # Try ISO format first
            dt = datetime.fromisoformat(time_str)
        except ValueError:
            # Try standard format
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        # Set source timezone
        from_tz = ZoneInfo(from_timezone)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=from_tz)

        # Convert to target timezone
        to_tz = ZoneInfo(to_timezone)
        converted = dt.astimezone(to_tz)

        return converted.isoformat()
    except Exception as e:
        return f"Error converting time: {str(e)}"


@mcp.tool()
def list_timezones(filter_str: Optional[str] = None) -> list[str]:
    """
    List available IANA timezone names.

    Args:
        filter_str: Optional string to filter timezone names (case-insensitive)

    Returns:
        List of timezone names

    Example:
        list_timezones("America") -> ["America/New_York", "America/Los_Angeles", ...]
    """
    timezones = sorted(available_timezones())

    if filter_str:
        timezones = [tz for tz in timezones if filter_str.lower() in tz.lower()]

    return timezones[:50]  # Limit to 50 results


@mcp.tool()
def get_timestamp() -> int:
    """
    Get the current Unix timestamp (seconds since epoch).

    Returns:
        Current Unix timestamp as integer
    """
    return int(datetime.now(timezone.utc).timestamp())


# Resources
@mcp.resource("datetime://{timezone}/now")
def get_datetime_resource(timezone: str) -> str:
    """
    Resource that provides current datetime for a specific timezone.

    URI pattern: datetime://America/New_York/now
    """
    try:
        if timezone not in available_timezones():
            return f"Error: Invalid timezone '{timezone}'"

        tz = ZoneInfo(timezone)
        current_time = datetime.now(tz)

        return f"Current time in {timezone}: {current_time.isoformat()}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.resource("datetime://utc/now")
def get_utc_now() -> str:
    """
    Resource that provides current UTC datetime.

    URI: datetime://utc/now
    """
    current_time = datetime.now(timezone.utc)
    return f"Current UTC time: {current_time.isoformat()}"


# Custom Routes
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint for monitoring."""
    return PlainTextResponse("OK")


@mcp.custom_route("/info", methods=["GET"])
async def server_info(request: Request) -> JSONResponse:
    """Server information endpoint."""
    return JSONResponse({
        "name": "ADK-MCP-Server",
        "version": "1.0.0",
        "transport": "streamable-http",
        "endpoint": "/adkmcp",
        "capabilities": {
            "tools": 4,
            "resources": 2,
            "prompts": 1
        }
    })


# Prompts
@mcp.prompt()
def current_time_prompt() -> str:
    """
    A prompt template for getting the current time.

    Returns a formatted prompt asking for the current time.
    """
    return """Please get the current time in multiple timezones:
1. UTC
2. America/New_York
3. Europe/London
4. Asia/Tokyo

Use the get_current_time tool to fetch these times."""


# Main entry point
def create_app():
    """
    Create and return the ASGI application for production deployment with CORS support.

    Usage with Uvicorn:
        uvicorn adkmcp_server:create_app --factory --host 0.0.0.0 --port 8000
    """
    # Define CORS middleware
    custom_middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify allowed origins
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["Mcp-Session-Id"],  # Required for browser-based MCP clients
        )
    ]

    # Create ASGI app with CORS middleware
    app = mcp.get_asgi_app(custom_middleware=custom_middleware)
    return app


if __name__ == "__main__":
    # Run the server with streamable-HTTP transport
    # The MCP endpoint will be available at http://localhost:8000/adkmcp
    # Note: HTTP transport has no authentication by default
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000,
        path="/adkmcp"  # Custom endpoint path
    )