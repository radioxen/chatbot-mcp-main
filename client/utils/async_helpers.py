import streamlit as st

# Helper function for running async functions
def run_async(coro):
    """Run an async function within the stored event loop."""
    return st.session_state.loop.run_until_complete(coro)

def reset_connection_state():
    """Reset all connection-related session state variables."""
    if 'client' in st.session_state and st.session_state.client is not None:
        try:
            # Close the existing client properly
            run_async(st.session_state.client.__aexit__(None, None, None))
        except Exception as e:
            st.error(f"Error closing previous client: {str(e)}")
    
    if 'client' in st.session_state:
        st.session_state.client = None
    if 'agent' in st.session_state:
        st.session_state.agent = None
    if 'tools' in st.session_state:
        st.session_state.tools = []

def on_shutdown():
    # Proper cleanup when the session ends
    try:
        if hasattr(st.session_state, 'client') and st.session_state.client is not None:
            try:
                # Close the client properly
                run_async(st.session_state.client.__aexit__(None, None, None))
            except Exception as e:
                print(f"Error during shutdown: {str(e)}")
    except Exception as e:
        print(f"Error accessing session state during shutdown: {str(e)}") 