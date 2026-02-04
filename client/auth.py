#!/usr/bin/env python3
"""
Streamlit Authentication Module
Provides API key-based authentication for the Voxies Streamlit app
"""
import streamlit as st
import os
import hashlib
import time
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_api_key():
    """Get the API key from environment variables"""
    return os.getenv('STREAMLIT_API_KEY')

def hash_api_key(api_key: str) -> str:
    """Create a hash of the API key for session storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def is_authenticated() -> bool:
    """Check if the current session is authenticated"""
    if 'authenticated' not in st.session_state:
        return False
    
    if 'auth_hash' not in st.session_state:
        return False
    
    # Check if authentication is still valid (24 hour session)
    if 'auth_timestamp' not in st.session_state:
        return False
    
    # Session expires after 24 hours
    if time.time() - st.session_state.auth_timestamp > 86400:
        logout()
        return False
    
    return st.session_state.authenticated

def authenticate(provided_key: str) -> bool:
    """Authenticate with the provided API key"""
    expected_key = get_api_key()
    
    if not expected_key:
        st.error("❌ Authentication not configured. Please contact administrator.")
        return False
    
    if provided_key == expected_key:
        st.session_state.authenticated = True
        st.session_state.auth_hash = hash_api_key(provided_key)
        st.session_state.auth_timestamp = time.time()
        return True
    else:
        st.session_state.authenticated = False
        if 'auth_hash' in st.session_state:
            del st.session_state.auth_hash
        if 'auth_timestamp' in st.session_state:
            del st.session_state.auth_timestamp
        return False

def logout():
    """Clear authentication session"""
    st.session_state.authenticated = False
    if 'auth_hash' in st.session_state:
        del st.session_state.auth_hash
    if 'auth_timestamp' in st.session_state:
        del st.session_state.auth_timestamp

def require_authentication():
    """
    Main authentication function to be called at the start of the app
    Returns True if authenticated, False if showing login screen
    """
    # Check if already authenticated
    if is_authenticated():
        return True
    
    # Show login screen
    st.set_page_config(
        page_title="Voxies Chatbot - Authentication",
        page_icon="🔐",
        layout='centered'
    )
    
    # Custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #f8f9fa;
    }
    .login-header {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Add Elder Voxie logo
        logo_path = os.path.join(os.path.dirname(__file__), 'icons', 'Elder Voxie Icon.png')
        if os.path.exists(logo_path):
            st.image(logo_path, width=120, use_container_width=False)
        
        st.markdown('<h1 class="login-header">🎮 Voxies Data Analytics</h1>', unsafe_allow_html=True)
        st.markdown('<h3 class="login-header">🔐 Authentication Required</h3>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # API Key input
        api_key = st.text_input(
            "Enter API Key:",
            type="password",
            placeholder="Enter your API key to access the application",
            help="Contact your administrator if you don't have an API key"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Access Application", use_container_width=True):
                if not api_key:
                    st.error("❌ Please enter an API key")
                elif authenticate(api_key):
                    st.success("✅ Authentication successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid API key. Please try again.")
                    time.sleep(2)
        
        st.markdown("---")
        
        # Information section
        with st.expander("ℹ️ About this Application"):
            st.markdown("""
            **Voxies Data Analytics Platform**
            
            This application provides access to:
            - 🎮 Game analytics and player insights
            - 📊 Real-time data visualization
            - 🤖 AI-powered data analysis
            - 💬 Interactive chat interface
            
            **Security Features:**
            - 🔐 API key authentication
            - 🕒 24-hour session timeout
            - 🛡️ Secure session management
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return False

def show_auth_status():
    """Show authentication status in sidebar"""
    if is_authenticated():
        with st.sidebar:
            st.success("🔐 Authenticated")
            
            # Show session info
            auth_time = st.session_state.get('auth_timestamp', 0)
            session_age = int((time.time() - auth_time) / 3600)  # hours
            remaining_hours = 24 - session_age
            
            st.caption(f"Session expires in {remaining_hours} hours")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun() 