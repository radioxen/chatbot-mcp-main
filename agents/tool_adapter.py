"""
Tool Adapter

Converts MCP tools to be compatible with LangChain's AgentExecutor
by handling the input format conversion from strings to JSON.
"""
import json
import re
from typing import List, Any, Dict
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class LangChainMCPToolAdapter(BaseTool):
    """
    Adapter that wraps MCP tools to be compatible with LangChain's AgentExecutor.
    
    Converts string inputs from LangChain to JSON inputs expected by MCP tools.
    """
    
    mcp_tool: Any = Field(description="The original MCP tool")
    
    def __init__(self, mcp_tool: Any, **kwargs):
        # Extract tool information from MCP tool
        name = mcp_tool.name
        description = mcp_tool.description
        
        # Create a schema based on the MCP tool's actual schema
        schema = getattr(mcp_tool, 'input_schema', {})
        properties = schema.get('properties', {})
        
        if not properties:
            # For tools with no parameters (like list_databases)
            class NoArgsSchema(BaseModel):
                pass
            args_schema = NoArgsSchema
        else:
            # Create dynamic schema based on MCP tool properties
            fields = {}
            for prop_name, prop_def in properties.items():
                field_type = str
                if prop_def.get('type') == 'integer':
                    field_type = int
                elif prop_def.get('type') == 'boolean':
                    field_type = bool
                
                fields[prop_name] = Field(
                    default=None if prop_name not in schema.get('required', []) else ...,
                    description=prop_def.get('description', f'{prop_name} parameter')
                )
            
            # Create dynamic schema class
            DynamicArgsSchema = type(f'{name}ArgsSchema', (BaseModel,), fields)
            args_schema = DynamicArgsSchema
        
        super().__init__(
            name=name,
            description=description,
            args_schema=args_schema,
            mcp_tool=mcp_tool,
            **kwargs
        )
    
    def _run(self, **kwargs) -> str:
        """
        Call the MCP tool with the provided keyword arguments.
        """
        try:
            print(f"DEBUG: Tool {self.name} called with kwargs: {kwargs}")
            
            # For tools with no parameters, use empty dict
            if not kwargs:
                args = {}
            else:
                # Filter out None values and prepare args
                args = {k: v for k, v in kwargs.items() if v is not None}
            
            print(f"DEBUG: Prepared args for {self.name}: {args}")
            
            # Call the original MCP tool with JSON args
            result = self.mcp_tool.invoke(args)
            print(f"DEBUG: Tool {self.name} result: {result}")
            return str(result)
            
        except Exception as e:
            print(f"DEBUG: Tool {self.name} error: {e}")
            import traceback
            traceback.print_exc()
            return f"Error calling tool {self.name}: {str(e)}"
    
    async def _arun(self, **kwargs) -> str:
        """Async version of _run"""
        try:
            print(f"DEBUG: Async tool {self.name} called with kwargs: {kwargs}")
            
            # For tools with no parameters, use empty dict
            if not kwargs:
                args = {}
            else:
                # Filter out None values and prepare args
                args = {k: v for k, v in kwargs.items() if v is not None}
            
            print(f"DEBUG: Async prepared args for {self.name}: {args}")
            
            # Call the original MCP tool with JSON args
            result = await self.mcp_tool.ainvoke(args)
            print(f"DEBUG: Async tool {self.name} result: {result}")
            return str(result)
            
        except Exception as e:
            print(f"DEBUG: Async tool {self.name} error: {e}")
            import traceback
            traceback.print_exc()
            return f"Error calling tool {self.name}: {str(e)}"
    
    def _parse_natural_language_input(self, input_str: str) -> Dict[str, Any]:
        """
        Parse natural language input into JSON parameters based on the tool's schema.
        """
        # Get the tool's input schema
        schema = getattr(self.mcp_tool, 'input_schema', {})
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        args = {}
        
        # For tools with no parameters (like list_databases)
        if not properties:
            return {}
        
        # Handle specific tool patterns
        if self.name == 'list_schemas':
            # Extract database name
            db_match = re.search(r'database[:\s]+([^\s,]+)', input_str, re.IGNORECASE)
            if db_match:
                args['database'] = db_match.group(1).strip('"\'')
            else:
                # Default to VOXIES if not specified
                args['database'] = 'VOXIES'
                
        elif self.name == 'list_tables':
            # Extract database and schema
            db_match = re.search(r'database[:\s]+([^\s,]+)', input_str, re.IGNORECASE)
            schema_match = re.search(r'schema[:\s]+([^\s,]+)', input_str, re.IGNORECASE)
            
            args['database'] = db_match.group(1).strip('"\'') if db_match else 'VOXIES'
            args['schema'] = schema_match.group(1).strip('"\'') if schema_match else 'ANALYTICS'
            
        elif self.name == 'describe_table':
            # Extract table name (could be fully qualified or just table name)
            table_match = re.search(r'table[:\s]+([^\s,]+(?:\.[^\s,]+)*)', input_str, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1).strip('"\'')
                # Ensure fully qualified name
                if '.' not in table_name:
                    table_name = f'VOXIES.ANALYTICS.{table_name}'
                elif table_name.count('.') == 1:
                    table_name = f'VOXIES.{table_name}'
                args['table_name'] = table_name
            else:
                # Try to extract any word that looks like a table name
                words = input_str.split()
                for word in words:
                    if word.upper() in ['BATTLES', 'PLAYERS', 'REWARDS', 'TOKENS', 'ITEMS']:
                        args['table_name'] = f'VOXIES.ANALYTICS.{word.upper()}'
                        break
                
        elif self.name == 'read_query':
            # The entire input is likely the SQL query
            # Clean up common prefixes
            query = input_str
            for prefix in ['query:', 'sql:', 'execute:', 'run:']:
                if query.lower().startswith(prefix):
                    query = query[len(prefix):].strip()
            args['query'] = query
            
        elif self.name == 'append_insight':
            # The entire input is the insight
            insight = input_str
            for prefix in ['insight:', 'note:', 'observation:']:
                if insight.lower().startswith(prefix):
                    insight = insight[len(prefix):].strip()
            args['insight'] = insight
        
        # Fill in any missing required parameters with defaults
        for param in required:
            if param not in args:
                if param == 'database':
                    args[param] = 'VOXIES'
                elif param == 'schema':
                    args[param] = 'ANALYTICS'
                elif param == 'query':
                    args[param] = input_str
                elif param == 'insight':
                    args[param] = input_str
        
        return args


def adapt_mcp_tools_for_langchain(mcp_tools: List[Any]) -> List[BaseTool]:
    """
    Convert a list of MCP tools to LangChain-compatible tools.
    
    Args:
        mcp_tools: List of MCP tools
        
    Returns:
        List of LangChain-compatible tools
    """
    adapted_tools = []
    
    for mcp_tool in mcp_tools:
        try:
            adapted_tool = LangChainMCPToolAdapter(mcp_tool)
            adapted_tools.append(adapted_tool)
        except Exception as e:
            print(f"Warning: Could not adapt tool {getattr(mcp_tool, 'name', 'unknown')}: {e}")
    
    return adapted_tools 