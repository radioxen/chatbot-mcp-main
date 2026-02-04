"""
Shared AI Agents Package

This package contains reusable AI agent implementations that can be used
across different interfaces (Streamlit, Slack, etc.)
"""

from .app_agent import AppAgent
from .mcp_client import MCPClientManager
from .tool_adapter import adapt_mcp_tools_for_langchain, LangChainMCPToolAdapter
from .prompts import make_system_prompt, make_main_prompt, get_react_prompt_template
from .llm_factory import LLMFactory
from .config import (
    DEFAULT_MAX_ITERATIONS, 
    DEFAULT_RECURSION_LIMIT, 
    DEFAULT_TEMPERATURE, 
    DEFAULT_MAX_TOKENS,
    MODEL_OPTIONS
)
from .tables import TABLES

__all__ = [
    'AppAgent', 
    'MCPClientManager', 
    'adapt_mcp_tools_for_langchain', 
    'LangChainMCPToolAdapter',
    'make_system_prompt',
    'make_main_prompt', 
    'get_react_prompt_template',
    'LLMFactory',
    'DEFAULT_MAX_ITERATIONS',
    'DEFAULT_RECURSION_LIMIT',
    'DEFAULT_TEMPERATURE',
    'DEFAULT_MAX_TOKENS',
    'MODEL_OPTIONS',
    'TABLES'
] 
