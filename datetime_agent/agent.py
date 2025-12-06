"""
DateTime Agent - Main Agent Definition

A Google ADK agent that connects to the FastMCP datetime server
to provide timezone and datetime assistance.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams
)

from .config import AgentConfig


# Agent Instructions
DATETIME_AGENT_INSTRUCTIONS = """
You are a helpful datetime and timezone assistant powered by specialized MCP tools.

Your capabilities include:
1. Getting the current time in any timezone
2. Converting times between different timezones
3. Listing available IANA timezones
4. Providing Unix timestamps
5. Answering questions about time zones, daylight saving time, and time conversions

Guidelines for providing assistance:
- Always use the MCP tools to get accurate, real-time information
- When users ask about "current time" without specifying a timezone, ask if they want UTC or their local timezone
- For timezone conversions, be explicit about the source and target timezones
- Use the list_timezones tool to help users find the correct IANA timezone name
- Provide clear, formatted responses with timezone abbreviations where helpful
- If a user's timezone name is invalid, use list_timezones with a filter to suggest corrections

Example interactions:
- "What time is it?" → Ask for timezone preference, then use get_current_time
- "Convert 3 PM EST to Tokyo time" → Use convert_time with America/New_York and Asia/Tokyo
- "What are the timezones in Europe?" → Use list_timezones with filter "Europe"
- "What's the Unix timestamp?" → Use get_timestamp

Always be helpful, accurate, and provide context for time-related information.
"""


# Agent Description
DATETIME_AGENT_DESCRIPTION = """
A specialized assistant for datetime and timezone queries.

This agent can:
- Get current time in any timezone
- Convert between timezones
- List available timezones
- Provide Unix timestamps
- Answer timezone-related questions

Powered by the FastMCP datetime server with access to the IANA timezone database.
"""


def create_datetime_agent() -> LlmAgent:
    """
    Create and configure the DateTime Agent.

    Returns:
        LlmAgent: Configured agent instance ready for use
    """
    # Validate configuration
    AgentConfig.validate()

    # Create the agent
    agent = LlmAgent(
        # Model configuration (Bedrock or Ollama) via LiteLLM
        model=LiteLlm(
            model=AgentConfig.get_model_identifier(),
            **AgentConfig.get_model_kwargs(),
        ),

        # Agent metadata
        name=AgentConfig.AGENT_NAME,
        description=DATETIME_AGENT_DESCRIPTION,

        # Agent behavior instructions
        instruction=DATETIME_AGENT_INSTRUCTIONS,

        # Tools - MCP Toolset connecting to FastMCP server
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=AgentConfig.MCP_SERVER_URL
                )
            )
        ],
    )

    return agent


# Create the singleton agent instance
# This is named 'root_agent' for compatibility with ADK web server
root_agent = create_datetime_agent()

# Also export as 'datetime_agent' for clarity
datetime_agent = root_agent


# Export for direct access
__all__ = ["root_agent", "datetime_agent", "create_datetime_agent"]
