import streamlit as st
import sys
import os
import traceback

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents import MODEL_OPTIONS
from services.streamlit_agent import StreamlitAppAgent
from services.chat_service import create_chat, delete_chat
from utils.tool_schema_parser import extract_tool_parameters
from utils.async_helpers import reset_connection_state


def create_history_chat_container():
    history_container = st.sidebar.container(height=200, border=None)
    with history_container:
        chat_history_menu = [
                f"{chat['chat_name']}_::_{chat['chat_id']}"
                for chat in st.session_state["history_chats"]
            ]
        chat_history_menu = chat_history_menu[:50][::-1]
        
        if chat_history_menu:
            current_chat = st.radio(
                label="History Chats",
                format_func=lambda x: x.split("_::_")[0] + '...' if "_::_" in x else x,
                options=chat_history_menu,
                label_visibility="collapsed",
                index=st.session_state["current_chat_index"],
                key="current_chat"
            )
            
            if current_chat:
                st.session_state['current_chat_id'] = current_chat.split("_::_")[1]


def create_sidebar_chat_buttons():
    """Create sidebar buttons for chat management."""
    if st.sidebar.button("🗑️ Clear All Chat", use_container_width=True, type="secondary"):
        st.session_state["history_chats"] = []
        st.session_state["messages"] = []
        st.session_state["current_chat_id"] = None
        st.session_state["tool_executions"] = []
        st.rerun()

def create_agent_settings_widget():
    """Create an expandable widget for agent limitations and settings."""
    with st.sidebar.expander("⚙️ Agent Settings", expanded=False):
        st.markdown("**LLM Call Limitations**")
        
        # Get current params
        params = st.session_state.get('params', {})
        
        # Max iterations setting
        max_iterations = st.number_input(
            "Max Iterations per Question",
            min_value=1,
            max_value=50,
            value=params.get('max_iterations', 10),
            help="Maximum number of agent steps before stopping"
        )
        
        # Recursion limit setting  
        recursion_limit = st.number_input(
            "Recursion Limit",
            min_value=5,
            max_value=100,
            value=params.get('recursion_limit', 25),
            help="LangGraph recursion limit (should be ~2.5x max iterations)"
        )
        
        st.markdown("**Development Mode**")
        
        # Development mode toggle
        dev_mode = st.checkbox(
            "Development Mode",
            value=params.get('dev_mode', True),
            help="Show detailed tool execution and debugging information"
        )
        
        # Tool visibility in dev mode
        show_tools = st.checkbox(
            "Show Tool Calls",
            value=params.get('show_tool_calls', True),
            disabled=not dev_mode,
            help="Display tool execution details (only in dev mode)"
        )
        
        # Supervisor verification visibility
        show_supervisor = st.checkbox(
            "Show Supervisor Verification",
            value=params.get('show_supervisor', True),
            disabled=not dev_mode,
            help="Display response verification steps (only in dev mode)"
        )
        
        # Update session state
        if 'params' not in st.session_state:
            st.session_state['params'] = {}
        st.session_state['params']['max_iterations'] = max_iterations
        st.session_state['params']['recursion_limit'] = recursion_limit
        st.session_state['params']['dev_mode'] = dev_mode
        st.session_state['params']['show_tool_calls'] = show_tools if dev_mode else False
        st.session_state['params']['show_supervisor'] = show_supervisor if dev_mode else False
        
        # Display current settings
        st.markdown("**Current Settings:**")
        st.text(f"Max Iterations: {max_iterations}")
        st.text(f"Recursion Limit: {recursion_limit}")
        st.text(f"Dev Mode: {'ON' if dev_mode else 'OFF'}")
        st.text(f"Tool Visibility: {'ON' if show_tools and dev_mode else 'OFF'}")
        st.text(f"Supervisor Info: {'ON' if show_supervisor and dev_mode else 'OFF'}")
        st.text(f"Estimated Max LLM Calls: {max_iterations * 2}")
        
        if recursion_limit < max_iterations * 2:
            st.warning("⚠️ Recursion limit should be at least 2x max iterations")
        
        # Reset to defaults button
        if st.button("Reset to Defaults", use_container_width=True):
            from agents import DEFAULT_MAX_ITERATIONS, DEFAULT_RECURSION_LIMIT
            # Default values for dev mode settings
            DEV_MODE = True
            SHOW_TOOL_CALLS_IN_DEV = True
            SHOW_SUPERVISOR_VERIFICATION = True
            
            st.session_state['params']['max_iterations'] = DEFAULT_MAX_ITERATIONS
            st.session_state['params']['recursion_limit'] = DEFAULT_RECURSION_LIMIT
            st.session_state['params']['dev_mode'] = DEV_MODE
            st.session_state['params']['show_tool_calls'] = SHOW_TOOL_CALLS_IN_DEV
            st.session_state['params']['show_supervisor'] = SHOW_SUPERVISOR_VERIFICATION
            st.rerun()

def create_model_select_widget():
    params = st.session_state["params"]
    params['model_id'] = st.sidebar.selectbox('🔎 Choose model',
                               options=MODEL_OPTIONS.keys(),
                               index=0)
    
def create_provider_select_widget():
    params = st.session_state.setdefault('params', {})
    # Load previously selected provider or default to the first
    default_provider = params.get("model_id", list(MODEL_OPTIONS.keys())[0])
    default_index = list(MODEL_OPTIONS.keys()).index(default_provider)
    # Provider selector with synced state
    selected_provider = st.sidebar.selectbox(
        '🔎 Choose Provider',
        options=list(MODEL_OPTIONS.keys()),
        index=default_index,
        key="provider_selection",
        on_change=reset_connection_state
    )
    # Save new provider and its index
    if selected_provider:
        params['model_id'] = selected_provider
        params['provider_index'] = list(MODEL_OPTIONS.keys()).index(selected_provider)
        st.sidebar.success(f"Model: {MODEL_OPTIONS[selected_provider]}")

    # Dynamic input fields based on provider
    with st.sidebar.container():
        if selected_provider == "Bedrock":
            with st.expander("🔐 Bedrock Credentials", expanded=True):
                params['region_name'] = st.text_input("AWS Region", value=params.get('region_name'),key="region_name")
                params['aws_access_key'] = st.text_input("AWS Access Key", value=params.get('aws_access_key'), type="password", key="aws_access_key")
                params['aws_secret_key'] = st.text_input("AWS Secret Key", value=params.get('aws_secret_key'), type="password", key="aws_secret_key")
        else:
            with st.expander("🔐 API Key", expanded=True):
                params['api_key'] = st.text_input(f"{selected_provider} API Key", value=params.get('api_key'), type="password", key="api_key")
    

def create_advanced_configuration_widget():
    params = st.session_state["params"]
    with st.sidebar.expander("⚙️  Basic config", expanded=False):
        params['max_tokens'] = st.number_input("Max tokens",
                                    min_value=1024,
                                    max_value=10240,
                                    value=4096,
                                    step=512,)
        params['temperature'] = st.slider("Temperature", 0.0, 1.0, step=0.05, value=1.0)
                
def create_mcp_connection_widget():
    with st.sidebar:
        st.subheader("Server Management")
        with st.expander(f"MCP Servers ({len(st.session_state.servers)})"):
            for name, config in st.session_state.servers.items():
                with st.container(border=True):
                    st.markdown(f"**Server:** {name}")
                    if 'url' in config:
                        st.markdown(f"**URL:** {config['url']}")
                    elif 'command' in config:
                        cmd_display = ' '.join([config['command']] + config.get('args', []))
                        st.markdown(f"**Command:** `{cmd_display}`")
                        if 'transport' in config:
                            st.markdown(f"**Transport:** {config['transport']}")
                    else:
                        st.markdown("**Config:** N/A")
                    if st.button(f"Remove {name}", key=f"remove_{name}"):
                        del st.session_state.servers[name]
                        st.rerun()

        if st.session_state.get("agent"):
            st.success(f"📶 Connected to {len(st.session_state.servers)} MCP servers!"
                       f" Found {len(st.session_state.tools)} tools.")
            if st.button("Disconnect to MCP Servers"):
                with st.spinner("Disconnecting from MCP servers..."):
                    try:
                        StreamlitAppAgent.disconnect_from_mcp_servers()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error disconnecting from MCP servers: {str(e)}")
                        st.code(traceback.format_exc(), language="python")
        else:
            st.warning("⚠️ Not connected to MCP server")
            if st.button("Connect to MCP Servers"):
                with st.spinner("Connecting to MCP servers..."):
                    try:
                        StreamlitAppAgent.connect_to_mcp_servers()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error connecting to MCP servers: {str(e)}")
                        st.code(traceback.format_exc(), language="python")

def create_mcp_tools_widget():
    with st.sidebar:
        if st.session_state.tools:
            st.subheader("🧰 Available Tools")

            selected_tool_name = st.selectbox(
                "Select a Tool",
                options=[tool.name for tool in st.session_state.tools],
                index=0
            )

            if selected_tool_name:
                selected_tool = next(
                    (tool for tool in st.session_state.tools if tool.name == selected_tool_name),
                    None
                )

                if selected_tool:
                    with st.container():
                        st.write("**Description:**")
                        st.write(selected_tool.description)

                        parameters = extract_tool_parameters(selected_tool)

                        if parameters:
                            st.write("**Parameters:**")
                            for param in parameters:
                                st.code(param)
