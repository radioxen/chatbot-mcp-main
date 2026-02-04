"""
Streamlit-specific wrapper for the shared AppAgent.

This provides Streamlit session state integration while using the exact same agent logic.
"""
import streamlit as st
import sys
import os
from typing import Dict, Optional

# Add agents directory to path (go up two levels from client/services/)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents import AppAgent, DEFAULT_MAX_ITERATIONS, DEFAULT_RECURSION_LIMIT
from utils.async_helpers import run_async

class StreamlitAppAgent:
    """
    Streamlit-specific wrapper for the shared AppAgent.
    Integrates with Streamlit session state while using shared agent logic.
    """
    
    @staticmethod
    def connect_to_mcp_servers():
        """Connect to MCP servers using shared agent (replaces mcp_service.connect_to_mcp_servers)"""
        # Clean up existing agent if any
        if "app_agent" in st.session_state:
            try:
                run_async(st.session_state.app_agent.cleanup())
            except Exception as e:
                st.warning(f"Error closing previous agent: {str(e)}")

        # Collect LLM config dynamically from session state
        params = st.session_state['params']
        llm_provider = params.get("model_id") or 'OpenAI'
        params.setdefault('model_id', llm_provider)
        params.setdefault('temperature', 1.0)
        params.setdefault('max_tokens', 4096)
        
        # Set LLM call limitations
        params.setdefault('max_iterations', DEFAULT_MAX_ITERATIONS)
        params.setdefault('recursion_limit', DEFAULT_RECURSION_LIMIT)
        
        # Create shared agent with Streamlit server config
        server_config = st.session_state.servers
        app_agent = AppAgent(server_config)
        
        try:
            # Initialize agent with Streamlit parameters
            run_async(app_agent.initialize(params))
            
            # Store in session state for compatibility with existing code
            st.session_state.app_agent = app_agent
            st.session_state.client = app_agent.mcp_manager.client
            st.session_state.tools = app_agent.get_tools()
            st.session_state.agent = app_agent.agent
            
        except Exception as e:
            st.error(f"Failed to initialize agent: {e}")
            st.stop()
            return

    @staticmethod
    def disconnect_from_mcp_servers():
        """Disconnect from MCP servers (replaces mcp_service.disconnect_from_mcp_servers)"""
        if "app_agent" in st.session_state:
            try:
                run_async(st.session_state.app_agent.cleanup())
            except Exception as e:
                st.warning(f"Error during disconnect: {str(e)}")
        else:
            st.info("No MCP connection to disconnect.")

        # Clean up session state
        st.session_state.app_agent = None
        st.session_state.client = None
        st.session_state.tools = []
        st.session_state.agent = None

    @staticmethod
    async def run_agent(agent, message: str, config: Dict = None) -> Dict:
        """
        Run the agent with the provided message (replaces mcp_service.run_agent)
        
        This is a compatibility wrapper that uses the shared agent's process_query method
        """
        # Get the shared agent from session state
        app_agent = st.session_state.get("app_agent")
        if not app_agent:
            raise Exception("App agent not initialized")
        
        try:
            return await app_agent.process_query(message, config)
        except Exception as e:
            # Handle recursion limit errors with Streamlit-specific UI
            if "recursion" in str(e).lower() or "GraphRecursionError" in str(e):
                params = st.session_state.get('params', {})
                recursion_limit = params.get('recursion_limit', DEFAULT_RECURSION_LIMIT)
                st.warning(f"⚠️ Agent reached maximum iterations ({recursion_limit//2} steps). The response may be incomplete.")
                return {
                    "messages": [{
                        "role": "assistant", 
                        "content": f"I've reached the maximum number of steps ({recursion_limit//2}) while processing your request. The analysis may be incomplete. Please try rephrasing your question or breaking it into smaller parts."
                    }]
                }
            else:
                raise e 
