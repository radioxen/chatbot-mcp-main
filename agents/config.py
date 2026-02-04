"""
Agent configuration settings
"""

# Development mode settings
DEV_MODE = True  # Debug mode: True
SHOW_TOOL_CALLS_IN_DEV = True  # Show tool execution details
SHOW_SUPERVISOR_VERIFICATION = True  # Show supervisor verification steps

# Agent settings
MAX_ITERATIONS = 20
VERBOSE = True

# Constants required by other modules
DEFAULT_MAX_ITERATIONS = 20
DEFAULT_RECURSION_LIMIT = 50
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

# Model configuration
MODEL_OPTIONS = {
    'OpenAI': 'gpt-4',
    'Antropic': 'claude-3-sonnet-20240229',
    'Bedrock': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'Google': 'gemini-pro'
}

# Snowflake MCP server configuration
SNOWFLAKE_SERVER_CONFIG = {
    "command": "python",
    "args": ["snowflake_launcher.py"],
    "env": {
        "SNOWFLAKE_ACCOUNT": "",  # Will be set from environment
        "SNOWFLAKE_USER": "",     # Will be set from environment  
        "SNOWFLAKE_PASSWORD": "", # Will be set from environment
        "SNOWFLAKE_DATABASE": "", # Will be set from environment
        "SNOWFLAKE_SCHEMA": "",   # Will be set from environment
        "SNOWFLAKE_WAREHOUSE": "" # Will be set from environment
    }
}
