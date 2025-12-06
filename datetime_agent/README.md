# DateTime Agent

A Google ADK agent that provides datetime and timezone assistance by connecting to the FastMCP datetime server.

## Overview

This agent uses Google's Agent Development Kit (ADK) to create a conversational AI assistant specialized in:
- Time queries across multiple timezones
- Timezone conversions
- Timezone information and lookups
- Unix timestamp generation

## Architecture

```
┌─────────────────────────────────────────┐
│  DateTime Agent (Google ADK)            │
│  - Ollama gemma3:4b (local LLM)         │
│  - LiteLLM model integration            │
└────────────────┬────────────────────────┘
                 │ MCP Protocol
                 │ (Streamable-HTTP)
                 v
┌─────────────────────────────────────────┐
│  FastMCP Server (adkmcp_server.py)      │
│  - Endpoint: /adkmcp                    │
│  - Tools: 4 datetime tools              │
│  - Resources: 2 datetime resources      │
└─────────────────────────────────────────┘
```

## Prerequisites

1. **Ollama Installed and Running**
   ```bash
   # Verify Ollama is running:
   curl http://localhost:11434/api/tags

   # Verify gemma3:4b is available:
   ollama list
   # Should show gemma3:4b in the list
   ```

2. **FastMCP Server Running**
   ```bash
   # From the mcp_file directory:
   cd mcp_file
   python adkmcp_server.py
   # Server runs at: http://localhost:8000/adkmcp
   ```

3. **Dependencies Installed**
   ```bash
   pip install -r requirements-agent.txt
   ```

## Configuration

Configuration is managed through environment variables in the `.env` file at the project root:

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_URL` | `http://localhost:8000/adkmcp` | MCP server endpoint |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma3:4b` | Ollama model to use |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Example .env File

```bash
# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8000/adkmcp

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b

# Logging
LOG_LEVEL=INFO
```

## Usage

### Primary: ADK Web Interface

The agent is designed to be used with the Google ADK Web interface for interactive testing and development.

1. **Start the ADK Web Server**
   ```bash
   # Make sure the MCP server is running first
   cd mcp_file
   python adkmcp_server.py

   # In another terminal, start ADK web server
   # (pointing to the agents/datetime_agent directory)
   adk web agents/datetime_agent
   ```

2. **Access the Web Interface**
   - Open your browser to the provided URL (typically `http://localhost:8080`)
   - Start chatting with the datetime agent
   - Try queries like:
     - "What time is it in Tokyo?"
     - "Convert 2 PM EST to London time"
     - "List timezones in Asia"

### Alternative: CLI Interactive Mode

For command-line testing, use the `run_agent.py` script:

```bash
python run_agent.py
```

This will start an interactive session where you can chat with the agent directly in your terminal.

### Programmatic Usage

```python
from agents.datetime_agent import datetime_agent

# Run a query
response = datetime_agent.run("What time is it in New York?")
print(response)
```

## Available MCP Tools

The agent has access to these tools from the FastMCP server:

### 1. `get_current_time(timezone_name: Optional[str])`
Get current time in a specific timezone or UTC.

**Example:**
```
User: What time is it in Tokyo?
Agent: The current time in Tokyo is [ISO timestamp]
```

### 2. `convert_time(time_str: str, from_timezone: str, to_timezone: str)`
Convert time between timezones.

**Example:**
```
User: Convert 3 PM EST to London time
Agent: 3:00 PM EST is 8:00 PM GMT in London
```

### 3. `list_timezones(filter_str: Optional[str])`
List available IANA timezones with optional filtering.

**Example:**
```
User: Show me timezones in Europe
Agent: Here are European timezones:
- Europe/London
- Europe/Paris
- Europe/Berlin
...
```

### 4. `get_timestamp()`
Get current Unix timestamp.

**Example:**
```
User: What's the current Unix timestamp?
Agent: The current Unix timestamp is 1733432445
```

## Example Conversations

**Query:** "What time is it in New York?"
```
Agent: The current time in New York is 2025-12-05 15:30:45 EST (UTC-5).
```

**Query:** "Convert 2 PM London time to Sydney"
```
Agent: 2:00 PM in London (Europe/London) is 1:00 AM the next day in Sydney (Australia/Sydney).
That's 2025-12-06T01:00:00+11:00 in ISO format.
```

**Query:** "List timezones in Asia"
```
Agent: Here are some timezones in Asia:
- Asia/Tokyo
- Asia/Singapore
- Asia/Dubai
- Asia/Kolkata
- Asia/Shanghai
... (and more)
```

## Testing

### Test MCP Server Connection

```bash
# Test server health
curl http://localhost:8000/health
# Should return: OK

# Test server info
curl http://localhost:8000/info
# Should return JSON with server information
```

### Test Ollama Connection

```bash
# Test Ollama is running
curl http://localhost:11434/api/tags

# Test gemma3:4b is available
ollama list | grep gemma3:4b
```

### Test Agent Creation

```python
from agents.datetime_agent import datetime_agent

print(f"Agent name: {datetime_agent.name}")
print(f"Agent description: {datetime_agent.description}")
```

### Test Agent Query

```python
from agents.datetime_agent import datetime_agent

response = datetime_agent.run("What's the current UTC time?")
print(response)
```

## Troubleshooting

### Common Issues

**1. MCP Server Not Running**
```
Error: Connection refused to http://localhost:8000/adkmcp
Solution: Start the FastMCP server first:
  cd mcp_file
  python adkmcp_server.py
```

**2. Ollama Not Running**
```
Error: Connection refused to http://localhost:11434
Solution: Start Ollama service or verify it's running:
  curl http://localhost:11434/api/tags
```

**3. Model Not Found**
```
Error: Model 'gemma3:4b' not found
Solution: Pull the model or verify it's installed:
  ollama pull gemma3:4b
  ollama list
```

**4. Invalid Timezone**
```
Error: Invalid timezone 'XYZ'
Solution: Use list_timezones tool to find correct timezone name:
  "List timezones containing XYZ"
```

**5. Import Error**
```
Error: ModuleNotFoundError: No module named 'google.adk'
Solution: Install dependencies:
  pip install -r requirements-agent.txt
```

## Development

### Project Structure
```
agents/datetime_agent/
├── __init__.py       # Package exports
├── agent.py          # Main agent definition
├── config.py         # Configuration management
└── README.md         # This file
```

### Extending the Agent

To add new capabilities:

1. **Add tools to MCP server** (`mcp_file/adkmcp_server.py`)
   - Use `@mcp.tool()` decorator to add new functions

2. **Update agent instructions** (in `agent.py`)
   - Add guidance for using new tools in `DATETIME_AGENT_INSTRUCTIONS`

3. **Agent automatically discovers new tools** via MCP protocol
   - No code changes needed in the agent itself

### Changing the Model

To use a different Ollama model:

1. **Pull the new model:**
   ```bash
   ollama pull mistral
   ```

2. **Update `.env` file:**
   ```bash
   OLLAMA_MODEL=mistral
   ```

3. **Restart the agent**

## References

- [Google ADK Documentation](https://github.com/google/adk)
- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol](https://github.com/modelcontextprotocol)
- [Ollama Documentation](https://ollama.ai/docs)
- [LiteLLM Documentation](https://docs.litellm.ai/)

## License

MIT License
