"""
Configuration management for DateTime Agent.

Handles environment variables and default settings for the agent.
"""

import os
from typing import Optional


class AgentConfig:
    """Configuration for the DateTime Agent."""

    # MCP Server Configuration
    MCP_SERVER_URL: str = os.getenv(
        "MCP_SERVER_URL",
        "http://localhost:8000/adkmcp"
    )

    # Model Provider Selection (ollama or bedrock)
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "bedrock")

    # Ollama Configuration (if using Ollama)
    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    OLLAMA_MODEL: str = os.getenv(
        "OLLAMA_MODEL",
        "gpt-oss"
    )

    # AWS Bedrock Configuration (if using Bedrock)
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    BEDROCK_MODEL: str = os.getenv(
        "BEDROCK_MODEL",
        "arn:aws:bedrock:us-east-1:590894668881:inference-profile/global.anthropic.claude-haiku-4-5-20251001-v1:0"
    )

    # Agent Metadata
    AGENT_NAME: str = "datetime_agent"
    AGENT_VERSION: str = "1.0.0"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_model_identifier(cls) -> str:
        """
        Get the model identifier for LiteLLM based on provider.

        Returns:
            Model identifier for LiteLLM
        """
        if cls.MODEL_PROVIDER.lower() == "bedrock":
            # For Bedrock, use the full ARN with bedrock/ prefix
            return f"bedrock/{cls.BEDROCK_MODEL}"
        else:
            # For Ollama
            return f"ollama/{cls.OLLAMA_MODEL}"

    @classmethod
    def get_model_kwargs(cls) -> dict:
        """
        Get additional model configuration kwargs.

        Returns:
            Dictionary of kwargs for LiteLlm model initialization
        """
        if cls.MODEL_PROVIDER.lower() == "bedrock":
            return {
                "aws_region_name": cls.AWS_REGION
            }
        else:
            return {
                "api_base": cls.OLLAMA_BASE_URL
            }

    @classmethod
    def validate(cls) -> None:
        """Validate configuration and print startup info."""
        print(f"[{cls.AGENT_NAME}] Configuration:")
        print(f"  MCP Server URL: {cls.MCP_SERVER_URL}")
        print(f"  Model Provider: {cls.MODEL_PROVIDER}")

        if cls.MODEL_PROVIDER.lower() == "bedrock":
            print(f"  AWS Region: {cls.AWS_REGION}")
            print(f"  Model: {cls.get_model_identifier()}")
        else:
            print(f"  Ollama Base URL: {cls.OLLAMA_BASE_URL}")
            print(f"  Model: {cls.get_model_identifier()}")

        print(f"  Version: {cls.AGENT_VERSION}")
        print(f"  Log Level: {cls.LOG_LEVEL}")
