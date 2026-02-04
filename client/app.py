"""
Streamlit MCP Playground - Enhanced with Elder Voxie Theme
"""
import streamlit as st
import asyncio
import os
import datetime
import traceback
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Apply nest_asyncio to allow nested asyncio event loops (needed for Streamlit's execution model)
import nest_asyncio
nest_asyncio.apply()

# Add agents directory to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Authentication
from auth import require_authentication, show_auth_status

# Check authentication first - if not authenticated, show login screen
if not require_authentication():
    st.stop()

# Core services
from services.chat_service import init_session, get_current_chat, _append_message_to_session
from services.streamlit_ai_service import get_response_stream
from services.streamlit_agent import StreamlitAppAgent
from utils.async_helpers import run_async
from utils.ai_prompts import make_system_prompt, make_main_prompt
from agents import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

# UI components
import ui_components.sidebar_components as sidebar_components
from ui_components.main_components import display_tool_executions

# LangChain imports
from langchain_core.messages import HumanMessage, ToolMessage

# Page configuration (only set if authenticated)
page_icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'Elder Voxie Icon.png')
st.set_page_config(
    page_title="Voxies Data Analytics",
    page_icon=page_icon_path,
    layout='wide',
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'style.css')
with open(css_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def main():
    # Initialize session state for event loop
    if "loop" not in st.session_state:
        st.session_state.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(st.session_state.loop)
    
    # Initialize the primary application
    init_session()
    
    # Sidebar components
    with st.sidebar:
        # Show authentication status
        show_auth_status()
        st.markdown("---")
        st.subheader("Chat History")
    sidebar_components.create_history_chat_container()
    
    # Main chat interface with Elder Voxie header
    col1, col2 = st.columns([1, 8])
    with col1:
        logo_path = os.path.join(os.path.dirname(__file__), 'icons', 'Elder Voxie Icon.png')
        st.image(logo_path, width=60, use_container_width=False)
    with col2:
        st.markdown('<div class="voxie-header"><h1 class="voxie-title">🎮 Voxies Data Analytics</h1></div>', unsafe_allow_html=True)
        st.markdown("*Ask me anything about Voxies game data, player statistics, battles, and token rewards!*")
    
    messages_container = st.container(height=400)
    
    # Re-render previous messages
    if st.session_state.get('current_chat_id'):
        st.session_state["messages"] = get_current_chat(st.session_state['current_chat_id'])
        for m in st.session_state["messages"]:
            with messages_container.chat_message(m["role"]):
                if "tool" in m and m["tool"]:
                    st.code(m["tool"], language='yaml')
                if "content" in m and m["content"]:
                    st.markdown(m["content"])
    
    # Chat input
    user_text = st.chat_input("Ask a question about Voxies game data or explore available analytics")
    
    # Sidebar widgets
    sidebar_components.create_sidebar_chat_buttons()
    sidebar_components.create_agent_settings_widget()
    
    # Auto-connect to MCP servers on first load
    if not st.session_state.get("agent"):
        # Use shared agent instead of direct mcp_service
        try:
            StreamlitAppAgent.connect_to_mcp_servers()
        except Exception as e:
            st.sidebar.error(f"Failed to connect to MCP servers: {e}")
    
    # Handle user input
    if user_text is None:
        st.stop()
    
    if user_text:
        # Add user message
        user_text_dct = {"role": "user", "content": user_text}
        _append_message_to_session(user_text_dct)
        with messages_container.chat_message("user"):
            st.markdown(user_text)
        
        # Process response with custom loading animation
        loading_placeholder = st.empty()
        with loading_placeholder:
            st.markdown("""
            <div class="voxie-loading magic-sparkles">
                <div class="voxie-spinner"></div>
                <h3>🔮 Elder Voxie is analyzing your data...</h3>
                <p><em>Casting spells on the Voxies database...</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        try:
            system_prompt = make_system_prompt()
            main_prompt = make_main_prompt(user_text)
            
            # Use agent if available
            if st.session_state.agent:
                response = run_async(StreamlitAppAgent.run_agent(st.session_state.agent, user_text))
                
                # Clear loading animation
                loading_placeholder.empty()
                
                # Get development mode settings
                params = st.session_state.get('params', {})
                dev_mode = params.get('dev_mode', True)
                show_tool_calls = params.get('show_tool_calls', True) and dev_mode
                show_supervisor = params.get('show_supervisor', True) and dev_mode
                
                # Extract tool executions
                if "messages" in response:
                    for msg in response["messages"]:
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                tool_output = next(
                                    (m.content for m in response["messages"] 
                                        if isinstance(m, ToolMessage) and 
                                        m.tool_call_id == tool_call['id']),
                                    None
                                )
                                if tool_output:
                                    st.session_state.tool_executions.append({
                                        "tool_name": tool_call['name'],
                                        "input": tool_call['args'],
                                        "output": tool_output,
                                        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    })
                
                # Process and display response
                output = ""
                tool_count = 0
                final_ai_message = None
                
                if "messages" in response:
                    for msg in response["messages"]:
                        # Handle dict format from our AppAgent
                        if isinstance(msg, dict):
                            if msg.get("role") == "assistant":
                                # Check if this is a tool message
                                if "tool" in msg and msg["tool"]:
                                    tool_count += 1
                                    if show_tool_calls:
                                        with messages_container.chat_message("assistant"):
                                            st.code(msg["tool"], language='yaml')
                                        _append_message_to_session({'role': 'assistant', 'tool': msg["tool"]})
                                elif "name" in msg:  # Tool message with name
                                    tool_count += 1
                                    if show_tool_calls:
                                        with messages_container.chat_message("assistant"):
                                            tool_message = f"**🔧 Tool Call {tool_count} ({msg['name']}):** \n" + msg.get("content", "")
                                            st.code(tool_message, language='yaml')
                                            _append_message_to_session({'role': 'assistant', 'tool': tool_message})
                                else:
                                    # Regular assistant message
                                    final_ai_message = msg.get("content", "")
                                    output = str(msg.get("content", ""))
                        # Handle LangChain message objects (fallback)
                        elif isinstance(msg, HumanMessage):
                            continue
                        elif hasattr(msg, 'name') and msg.name:  # ToolMessage
                            tool_count += 1
                            if show_tool_calls:
                                with messages_container.chat_message("assistant"):
                                    tool_message = f"**🔧 Tool Call {tool_count} ({msg.name}):** \n" + msg.content
                                    st.code(tool_message, language='yaml')
                                    _append_message_to_session({'role': 'assistant', 'tool': tool_message})
                        else:  # AIMessage
                            if hasattr(msg, "content") and msg.content:
                                final_ai_message = msg.content
                                output = str(msg.content)
                
                # Supervisor verification layer
                if show_supervisor and final_ai_message:
                    with messages_container.chat_message("assistant"):
                        st.markdown("### 🔍 **Supervisor Verification**")
                        
                        verification_checks = [
                            ("✅ Data-driven response", "based on actual queries" in output.lower() or "query" in output.lower()),
                            ("✅ Table structures verified", tool_count > 0 and any("describe_table" in str(exec.get('tool_name', '')) for exec in st.session_state.tool_executions[-5:])),
                            ("✅ Results are realistic", len(output) > 50 and not any(word in output.lower() for word in ["assume", "estimate", "approximately", "roughly"])),
                            ("✅ Methodology explained", "analysis" in output.lower() or "method" in output.lower() or "approach" in output.lower()),
                            ("✅ Limitations mentioned", "limitation" in output.lower() or "caveat" in output.lower() or "note" in output.lower()),
                            ("✅ Follow-up suggestions", "suggest" in output.lower() or "recommend" in output.lower() or "next" in output.lower())
                        ]
                        
                        passed_checks = sum(1 for _, check in verification_checks if check)
                        total_checks = len(verification_checks)
                        
                        for criterion, passed in verification_checks:
                            if passed:
                                st.success(criterion)
                            else:
                                st.warning(criterion.replace("✅", "⚠️"))
                        
                        score = (passed_checks / total_checks) * 100
                        if score >= 80:
                            st.success(f"**Verification Score: {score:.0f}%** - High quality response ✅")
                        elif score >= 60:
                            st.warning(f"**Verification Score: {score:.0f}%** - Acceptable response ⚠️")
                        else:
                            st.error(f"**Verification Score: {score:.0f}%** - Response needs improvement ❌")
                
                # Display final response
                if output:
                    with messages_container.chat_message("assistant"):
                        if not show_supervisor:
                            st.markdown("### 📊 **Analysis Results**")
                        st.markdown(output)
                
                response_dct = {"role": "assistant", "content": output}
            
            # Fallback to regular stream response
            else:
                loading_placeholder.empty()
                st.warning("You are not connected to MCP servers!")
                response_stream = get_response_stream(
                    main_prompt,
                    llm_provider=st.session_state['params']['model_id'],
                    system=system_prompt,
                    temperature=st.session_state['params'].get('temperature', DEFAULT_TEMPERATURE),
                    max_tokens=st.session_state['params'].get('max_tokens', DEFAULT_MAX_TOKENS)
                )
                with messages_container.chat_message("assistant"):
                    response = st.write_stream(response_stream)
                    response_dct = {"role": "assistant", "content": response}
                    
        except Exception as e:
            loading_placeholder.empty()
            response = f"⚠️ Something went wrong: {str(e)}"
            st.error(response)
            st.code(traceback.format_exc(), language="python")
            st.stop()
        
        # Add assistant message to chat history
        _append_message_to_session(response_dct)
    
    # Display tool executions
    display_tool_executions()


if __name__ == "__main__":
    main()
