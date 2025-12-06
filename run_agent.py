#!/usr/bin/env python3
"""
DateTime Agent - Interactive Runner

Run the Google ADK DateTime Agent in interactive mode.

Usage:
    python run_agent.py

Prerequisites:
    1. MCP server running at http://localhost:8000/adkmcp
    2. Ollama running with gemma3:4b model
    3. Dependencies installed: pip install -r requirements-agent.txt
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from agents.datetime_agent import datetime_agent


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("  DateTime Agent - Interactive Mode")
    print("  Powered by Google ADK + FastMCP + Ollama")
    print("=" * 60)
    print("\nCommands:")
    print("  - Type your question and press Enter")
    print("  - Type 'exit', 'quit', or 'q' to end session")
    print("  - Press Ctrl+C to interrupt")
    print("\nExample queries:")
    print("  - What time is it in Tokyo?")
    print("  - Convert 3 PM EST to London time")
    print("  - List timezones in Europe")
    print("  - What's the current Unix timestamp?")
    print("\n" + "=" * 60 + "\n")


def check_prerequisites():
    """Check if prerequisites are met."""
    import requests

    all_ok = True

    # Check MCP server
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/adkmcp")
    server_base = mcp_url.rsplit("/", 1)[0]

    try:
        response = requests.get(f"{server_base}/health", timeout=2)
        if response.status_code == 200:
            print(f"[OK] MCP Server is running at {server_base}")
        else:
            print(f"[WARNING] MCP Server responded with status {response.status_code}")
            all_ok = False
    except requests.RequestException as e:
        print(f"[ERROR] Cannot connect to MCP server at {server_base}")
        print(f"        Please start the server: python mcp_file/adkmcp_server.py")
        all_ok = False

    # Check Ollama server
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            print(f"[OK] Ollama is running at {ollama_url}")

            # Check if gemma3:4b is available
            models = response.json().get("models", [])
            model_name = os.getenv("OLLAMA_MODEL", "gemma3:4b")
            model_found = any(model.get("name", "").startswith(model_name) for model in models)

            if model_found:
                print(f"[OK] Model '{model_name}' is available")
            else:
                print(f"[WARNING] Model '{model_name}' not found")
                print(f"          Run: ollama pull {model_name}")
                all_ok = False
        else:
            print(f"[WARNING] Ollama responded with status {response.status_code}")
            all_ok = False
    except requests.RequestException as e:
        print(f"[ERROR] Cannot connect to Ollama at {ollama_url}")
        print(f"        Please ensure Ollama is installed and running")
        print(f"        Visit: https://ollama.ai/download")
        all_ok = False

    print()
    return all_ok


def main():
    """Main interactive loop."""
    print_banner()

    # Check prerequisites
    if not check_prerequisites():
        print("\nPlease resolve the issues above and try again.")
        response = input("\nContinue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return 1

    print("Ready! Ask me anything about time and timezones.\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break

            # Skip empty input
            if not user_input:
                continue

            # Run the agent
            print("\nAgent: ", end="", flush=True)
            try:
                response = datetime_agent.run(user_input)
                print(f"{response}\n")
            except Exception as e:
                print(f"\n[ERROR] Agent error: {type(e).__name__}: {e}\n")
                print("This might be due to:")
                print("  - MCP server not running")
                print("  - Ollama not running")
                print("  - Network connectivity issues")
                print("  - Model configuration issues\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] {type(e).__name__}: {e}\n")
            import traceback
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
