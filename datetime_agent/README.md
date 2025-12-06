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
│  - AWS Bedrock / Claude Haiku 4.5       │
│  - LiteLLM model integration            │
│  - Phoenix Arize tracing enabled        │
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
                 │
                 │ OpenTelemetry Traces
                 v
┌─────────────────────────────────────────┐
│  Phoenix Arize (localhost:6006)         │
│  - LLM call tracing                     │
│  - Tool usage monitoring                │
│  - Performance analytics                │
└─────────────────────────────────────────┘
```

## Prerequisites

1. **AWS Bedrock Access** (or Ollama for local models)
   - AWS credentials configured for Bedrock
   - Claude Haiku 4.5 model access enabled
   - OR: Ollama installed with a tool-capable model (gpt-oss, llama3, mistral)

2. **FastMCP Server Running**
   ```bash
   # From the mcp_file directory:
   cd mcp_file
   python adkmcp_server.py
   # Server runs at: http://localhost:8000/adkmcp
   ```

3. **Phoenix Arize** (Optional - for tracing/observability)
   ```bash
   # Phoenix running in Docker on port 6006
   # Visit http://localhost:6006 to view traces
   ```

4. **Dependencies Installed**
   ```bash
   pip install -r requirements-agent.txt
   ```

## Configuration

Configuration is managed through environment variables in the `.env` file at the project root:

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_URL` | `http://localhost:8000/adkmcp` | MCP server endpoint |
| `MODEL_PROVIDER` | `bedrock` | Model provider: "bedrock" or "ollama" |
| **AWS Bedrock Settings** | | |
| `AWS_REGION` | `us-east-1` | AWS region for Bedrock |
| `BEDROCK_MODEL` | `arn:aws:bedrock:...` | Full Bedrock model ARN |
| `AWS_BEARER_TOKEN_BEDROCK` | - | AWS bearer token for authentication |
| **Ollama Settings** | | |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gpt-oss` | Ollama model to use |
| **Phoenix Tracing** | | |
| `PHOENIX_ENABLED` | `true` | Enable/disable Phoenix tracing |
| `PHOENIX_COLLECTOR_ENDPOINT` | `http://localhost:6006` | Phoenix collector URL |
| `PHOENIX_PROJECT_NAME` | `adk-mcp-agent-tracing` | Project name in Phoenix |
| `PHOENIX_TRACES_ENDPOINT` | `http://localhost:6006/v1/traces` | Phoenix traces endpoint |
| **Other** | | |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `DEBUG` | `false` | Enable debug mode |

### Example .env File

```bash
# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8000/adkmcp

# Model Provider
MODEL_PROVIDER=bedrock  # or "ollama"

# AWS Bedrock Configuration (if using Bedrock)
AWS_REGION=us-east-1
BEDROCK_MODEL=arn:aws:bedrock:us-east-1:590894668881:inference-profile/global.anthropic.claude-haiku-4-5-20251001-v1:0
AWS_BEARER_TOKEN_BEDROCK=your-bearer-token-here

# Ollama Configuration (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss

# Phoenix Arize Tracing
PHOENIX_ENABLED=true
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
PHOENIX_PROJECT_NAME=adk-mcp-agent-tracing
PHOENIX_TRACES_ENDPOINT=http://localhost:6006/v1/traces

# Logging
LOG_LEVEL=DEBUG
DEBUG=true
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

## Phoenix Arize Tracing

The agent includes built-in support for Phoenix Arize, an observability platform for LLM applications that provides detailed tracing of:
- LLM calls and responses
- Tool invocations (MCP tools)
- Latency and performance metrics
- Token usage and costs

### Setup Phoenix

1. **Run Phoenix in Docker:**
   ```bash
   docker run -p 6006:6006 arizephoenix/phoenix:latest
   ```

2. **Access Phoenix UI:**
   - Open http://localhost:6006 in your browser
   - You'll see the Phoenix dashboard

3. **Configure the Agent:**
   Phoenix is enabled by default. The configuration is already set in `.env`:
   ```bash
   PHOENIX_ENABLED=true
   PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
   PHOENIX_PROJECT_NAME=adk-mcp-agent-tracing
   PHOENIX_TRACES_ENDPOINT=http://localhost:6006/v1/traces
   ```

### Using Phoenix

Once the agent is running with Phoenix enabled, you'll see:

1. **Automatic Instrumentation:**
   - All LLM calls to Claude Haiku are traced
   - MCP tool invocations are recorded
   - Request/response pairs are captured

2. **Phoenix Dashboard Features:**
   - **Traces View:** See all LLM interactions in real-time
   - **Projects:** Organize traces by project (adk-mcp-agent-tracing)
   - **Performance:** Analyze latency, token usage, and costs
   - **Debugging:** Inspect full request/response payloads

3. **Example Trace Information:**
   ```
   Trace: "What time is it in Tokyo?"
   ├─ LLM Call (Claude Haiku)
   │  ├─ Input: User query + system instructions
   │  ├─ Tool Selection: get_current_time
   │  └─ Duration: 1.2s, Tokens: 245
   ├─ MCP Tool Call
   │  ├─ Tool: get_current_time("Asia/Tokyo")
   │  ├─ Response: "2025-12-06T08:42:00+09:00"
   │  └─ Duration: 15ms
   └─ LLM Response Generation
      ├─ Output: Formatted response to user
      └─ Duration: 0.8s, Tokens: 128
   ```

### Disabling Phoenix

To disable Phoenix tracing:

1. **Update `.env`:**
   ```bash
   PHOENIX_ENABLED=false
   ```

2. **Restart the agent**

The agent will continue to function normally without tracing.

### Phoenix Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PHOENIX_ENABLED` | `true` | Enable/disable Phoenix tracing |
| `PHOENIX_COLLECTOR_ENDPOINT` | `http://localhost:6006` | Phoenix collector URL |
| `PHOENIX_PROJECT_NAME` | `adk-mcp-agent-tracing` | Project name in Phoenix UI |
| `PHOENIX_TRACES_ENDPOINT` | `http://localhost:6006/v1/traces` | OTEL traces endpoint |

### Benefits

Phoenix Arize tracing provides:
- **Debugging:** Quickly identify issues with LLM responses or tool calls
- **Optimization:** Analyze latency bottlenecks and optimize performance
- **Cost Tracking:** Monitor token usage and associated costs
- **Quality Assurance:** Review LLM outputs for quality and consistency
- **Analytics:** Understand usage patterns and user interactions

For more information, visit: https://docs.arize.com/phoenix

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
