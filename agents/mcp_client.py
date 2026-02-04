"""
MCP Client Manager

Shared MCP client logic extracted from client/services/mcp_service.py
for use across different interfaces (Streamlit, Slack, etc.)
"""
import os
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Add client directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection
from langchain_core.tools import BaseTool
from .config import DEFAULT_MAX_ITERATIONS, DEFAULT_RECURSION_LIMIT

load_dotenv()

class MCPClientManager:
    """
    Manages MCP client connections and tool access.
    Extracted from client/services/mcp_service.py for reuse across interfaces.
    """
    
    def __init__(self, server_config: Optional[Dict] = None):
        self.client: Optional[MultiServerMCPClient] = None
        self.tools: List[BaseTool] = []
        self.server_config = server_config or self._get_default_server_config()
        self.connected = False
    
    def _get_default_server_config(self) -> Dict:
        """Get default server configuration"""
        # Get the path to snowflake_launcher.py in the same agents directory
        snowflake_launcher_path = os.path.join(os.path.dirname(__file__), 'snowflake_launcher.py')
        
        # Ensure environment variables are loaded
        snowflake_env_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER", 
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_WAREHOUSE",
            "SNOWFLAKE_ROLE",
            "SNOWFLAKE_DATABASE",
            "SNOWFLAKE_SCHEMA",
        ]
        
        # Collect environment variables for the subprocess
        env_vars = {k: os.getenv(k) for k in snowflake_env_vars if os.getenv(k)}
        
        return {
            "snowflake": {
                "command": "python",
                "args": [snowflake_launcher_path],
                "transport": "stdio",
                "env": env_vars
            }
        }
    
    def _check_snowflake_env_vars(self) -> None:
        """Check that all required Snowflake environment variables are present"""
        snowflake_env_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER", 
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_WAREHOUSE",
            "SNOWFLAKE_ROLE",
            "SNOWFLAKE_DATABASE",
            "SNOWFLAKE_SCHEMA",
        ]
        
        missing_vars = [var for var in snowflake_env_vars if not os.getenv(var)]
        if missing_vars:
            raise Exception(f"Missing required Snowflake environment variables: {', '.join(missing_vars)}")
        
        # Set environment variables for stdio-based servers (same as mcp_service.py)
        for cfg in self.server_config.values():
            if cfg.get("transport") == "stdio":
                env_vars = {k: os.getenv(k) for k in snowflake_env_vars if os.getenv(k)}
                cfg["env"] = env_vars
                # Also ensure they're available in the current process environment
                for k, v in env_vars.items():
                    if v:
                        os.environ[k] = v
    
    async def connect(self) -> None:
        """Connect to MCP servers and get available tools"""
        if self.connected:
            return
        
        self._check_snowflake_env_vars()
        
        # Create proper connections using StdioConnection for the new API
        connections = {}
        for server_name, config in self.server_config.items():
            if config.get("transport") == "stdio":
                # Use StdioConnection to create proper connection object and add transport key
                connection = StdioConnection(
                    command=config["command"],
                    args=config["args"],
                    env=config.get("env", {})
                )
                # Add the transport key that create_session expects
                connection["transport"] = "stdio"
                connections[server_name] = connection
        
        # Pass the properly formatted connections to MultiServerMCPClient
        self.client = MultiServerMCPClient(connections=connections)
        
        # Get tools from MCP server using the new API
        self.tools = await self.client.get_tools()
        self.connected = True
    
    async def disconnect(self) -> None:
        """Disconnect from MCP servers"""
        if self.client and self.connected:
            try:
                # The new API doesn't require explicit disconnection
                pass
            except Exception as e:
                print(f"⚠️ Error during MCP disconnect: {str(e)}")
        
        self.client = None
        self.tools = []
        self.connected = False
    
    def get_tools(self) -> List[BaseTool]:
        """Get available tools from connected MCP servers"""
        if not self.connected:
            raise Exception("MCP client not connected. Call connect() first.")
        return self.tools
    
    def is_connected(self) -> bool:
        """Check if MCP client is connected"""
        return self.connected and self.client is not None 