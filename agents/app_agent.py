"""
App Agent

Shared AI agent implementation extracted from client/services/mcp_service.py
and slack_bot/core_agent.py for use across different interfaces.
"""
import os
import sys
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Add client directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import from local config
from .config import DEFAULT_MAX_ITERATIONS, DEFAULT_RECURSION_LIMIT
from .llm_factory import LLMFactory
from .mcp_client import MCPClientManager
from .prompts import get_react_prompt_template

load_dotenv()

class AppAgent:
    """
    App data agent that provides consistent behavior across all interfaces.
    
    Uses OpenAI Functions agent for better structured tool calling compatibility.
    """
    
    def __init__(self, server_config: Optional[Dict] = None):
        self.mcp_manager = MCPClientManager(server_config)
        self.agent = None
        self.params = None
        self.initialized = False
    
    async def initialize(self, params: Optional[Dict] = None) -> None:
        """
        Initialize the agent with MCP client and LLM.
        
        Args:
            params: Agent parameters (model_id, temperature, etc.)
                   If None, uses default parameters
        """
        if self.initialized:
            return
        
        # Set default parameters (same as mcp_service.py)
        self.params = params or {
            'model_id': 'OpenAI',
            'temperature': 0.3,  # Lower temperature for better format adherence
            'max_tokens': 4096,
            'max_iterations': DEFAULT_MAX_ITERATIONS,
            'recursion_limit': DEFAULT_RECURSION_LIMIT
        }
        
        # Ensure all required parameters are present
        self.params.setdefault('model_id', 'OpenAI')
        self.params.setdefault('temperature', 0.3)
        self.params.setdefault('max_tokens', 4096)
        self.params.setdefault('max_iterations', DEFAULT_MAX_ITERATIONS)
        self.params.setdefault('recursion_limit', DEFAULT_RECURSION_LIMIT)
        
        # Connect to MCP servers
        await self.mcp_manager.connect()
        mcp_tools = self.mcp_manager.get_tools()
        
        print(f"DEBUG: Retrieved {len(mcp_tools)} MCP tools")
        for tool in mcp_tools:
            print(f"  - {getattr(tool, 'name', 'unknown')}: {getattr(tool, 'description', 'no description')}")
        
        # Use MCP tools directly - they should already be LangChain compatible
        tools = mcp_tools
        
        print(f"DEBUG: Using {len(tools)} tools directly for LangChain")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Create LLM using shared factory
        try:
            llm = LLMFactory.create_llm(
                llm_provider=self.params['model_id'],
                config={},  # Config will come from environment variables
                temperature=self.params['temperature'], 
                max_tokens=self.params['max_tokens']
            )
            print(f"DEBUG: LLM created successfully: {type(llm)}")
        except Exception as e:
            print(f"DEBUG: LLM creation failed: {e}")
            raise Exception(f"Failed to initialize LLM: {e}")
        
        # Create OpenAI Functions agent instead of React agent
        # Use ChatPromptTemplate for Functions agent with proper system prompt
        system_prompt = """You are a Voxies game analytics assistant. You are an expert data analyst and SQL specialist.

CRITICAL BEHAVIOR:
- For data questions: ALWAYS query the database first - be proactive and analytical
- For general questions about game rules/mechanics: Answer directly without database queries
- NEVER make assumptions or hallucinate data - always verify with actual queries

ANALYTICAL APPROACH:
- When asked about counts, statistics, or specific data: IMMEDIATELY start with list_databases, then explore schemas and tables
- ALWAYS use describe_table before any read_query to verify column names
- For questions like "how many classes" or "what classes exist": Query the data to get exact counts and lists
- Be thorough - if initial query doesn't answer fully, do follow-up queries
- Present data in clear, structured format with actual numbers and lists

WORKFLOW for data questions:
1. Start with list_databases to see available databases
2. Use list_schemas and list_tables to explore structure  
3. Use describe_table to verify exact column names
4. Build precise read_query with correct SQL syntax
5. If needed, do follow-up queries for complete analysis
6. Present findings with actual data, not estimates

EXAMPLES:
- "How many voxie classes are there?" → Query database to get distinct count of CLASS column
- "What classes exist?" → Query to get full list of unique classes
- "Show me player stats" → Explore tables, verify columns, query actual data

Remember: Be proactive, analytical, and data-driven. Always verify with real queries."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create OpenAI Functions agent and executor
        agent = create_openai_functions_agent(llm, tools, prompt)
        self.agent = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True,  # Enable verbose mode for debugging
            handle_parsing_errors=True,
            return_intermediate_steps=True,  # This is crucial for capturing tool calls
            max_iterations=self.params.get('max_iterations', DEFAULT_MAX_ITERATIONS)
        )
        
        print(f"DEBUG: Agent executor created successfully")
        self.initialized = True
    
    async def process_query(self, message: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user query using the OpenAI Functions agent.
        
        Args:
            message: User message/query
            config: Optional configuration (recursion_limit, etc.)
            
        Returns:
            Dictionary containing agent response
        """
        if not self.initialized:
            raise Exception("Agent not initialized. Call initialize() first.")
        
        try:
            print(f"DEBUG: Processing query: {message}")
            print(f"DEBUG: Agent initialized: {self.initialized}")
            print(f"DEBUG: Available tools: {[tool.name for tool in self.agent.tools]}")
            print(f"DEBUG: Agent type: {type(self.agent)}")
            print(f"DEBUG: Agent config: max_iterations={self.agent.max_iterations}, verbose={self.agent.verbose}")
            
            # Use AgentExecutor with input parameter
            print(f"DEBUG: Calling agent.ainvoke with input: {message}")
            response = await self.agent.ainvoke({"input": message})
            
            print(f"DEBUG: Raw agent response: {response}")
            print(f"DEBUG: Response type: {type(response)}")
            print(f"DEBUG: Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
            
            # Convert AgentExecutor response to expected format
            if isinstance(response, dict):
                if "output" in response:
                    print(f"DEBUG: Found output in response: {response['output']}")
                    output_content = response["output"]
                elif "result" in response:
                    print(f"DEBUG: Found result in response: {response['result']}")
                    output_content = response["result"]
                else:
                    print(f"DEBUG: No output/result field found, using full response")
                    output_content = str(response)
                
                # Check if we have intermediate steps that show tool usage
                messages = []
                if "intermediate_steps" in response:
                    print(f"DEBUG: Found {len(response['intermediate_steps'])} intermediate steps")
                    for i, step in enumerate(response['intermediate_steps']):
                        print(f"DEBUG: Step {i}: {step}")
                        # Add tool calls as separate messages for Streamlit to display
                        if hasattr(step, '__len__') and len(step) >= 2:
                            action, observation = step[0], step[1]
                            if hasattr(action, 'tool') and hasattr(action, 'tool_input'):
                                # Create a tool message format that Streamlit expects
                                tool_msg = {
                                    "role": "assistant",
                                    "content": f"🔧 **Tool: {action.tool}**\nInput: {action.tool_input}\nOutput: {observation}",
                                    "tool": f"**{action.tool}**: {action.tool_input}\n\nResult: {observation}",
                                    "name": action.tool
                                }
                                messages.append(tool_msg)
                
                # Add the final response
                messages.append({
                    "role": "assistant",
                    "content": output_content
                })
                
                return {"messages": messages}
            else:
                print(f"DEBUG: Response is not a dict, using raw response")
                return {
                    "messages": [{
                        "role": "assistant", 
                        "content": str(response)
                    }]
                }
                
        except Exception as e:
            print(f"DEBUG: Exception in process_query: {e}")
            print(f"DEBUG: Exception type: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            
            # Handle parsing errors gracefully (should be handled by handle_parsing_errors=True)
            if "OutputParserException" in str(e) or "parse" in str(e).lower():
                return {
                    "messages": [{
                        "role": "assistant", 
                        "content": f"I encountered a formatting issue while processing your request. Let me try to help you directly. What specific information about the Voxies game data would you like to know?"
                    }],
                    "warning": "Agent output parsing error occurred"
                }
            
            # Handle recursion limit errors gracefully
            recursion_limit = self.params.get('recursion_limit', DEFAULT_RECURSION_LIMIT)
            if "recursion" in str(e).lower() or "maximum" in str(e).lower():
                warning_msg = f"Agent reached maximum iterations ({recursion_limit//2} steps). The response may be incomplete."
                return {
                    "messages": [{
                        "role": "assistant", 
                        "content": f"I've reached the maximum number of steps ({recursion_limit//2}) while processing your request. The analysis may be incomplete. Please try rephrasing your question or breaking it into smaller parts."
                    }],
                    "warning": warning_msg
                }
            else:
                raise e
    
    def extract_response_content(self, response: Dict[str, Any]) -> tuple[str, int]:
        """
        Extract the final response content and tool count from agent response.
        
        Args:
            response: Response from process_query()
            
        Returns:
            Tuple of (response_content, tool_count)
        """
        output = ""
        tool_count = 0
        
        if "messages" in response:
            for msg in response["messages"]:
                if isinstance(msg, dict):
                    # Handle dict format from AgentExecutor
                    if msg.get("role") == "assistant":
                        output = str(msg.get("content", ""))
                elif isinstance(msg, HumanMessage):
                    continue
                elif hasattr(msg, 'name') and msg.name:  # ToolMessage
                    tool_count += 1
                else:  # AIMessage
                    if hasattr(msg, "content") and msg.content:
                        output = str(msg.content)
        
        # For AgentExecutor, we don't have direct tool count access, so estimate based on response complexity
        if not tool_count and output and len(output) > 100:
            tool_count = 1  # Assume at least one tool was used for complex responses
        
        return output, tool_count
    
    async def cleanup(self) -> None:
        """Clean up agent resources"""
        await self.mcp_manager.disconnect()
        self.agent = None
        self.initialized = False
    
    def is_initialized(self) -> bool:
        """Check if agent is initialized"""
        return self.initialized and self.mcp_manager.is_connected()
    
    def get_tools(self) -> List[BaseTool]:
        """Get available tools"""
        return self.mcp_manager.get_tools()
    
    def get_params(self) -> Optional[Dict]:
        """Get current agent parameters"""
        return self.params 
