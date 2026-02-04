"""
Streamlit-specific AI service wrapper.

This module provides Streamlit-specific LLM functionality while using the shared LLMFactory.
"""
import streamlit as st
import sys
import os
from typing import Optional

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents import LLMFactory


def create_llm_model(llm_provider: str, **kwargs):
    """Create a language model using Streamlit session state for configuration."""
    params = st.session_state.get('params', {})
    
    try:
        return LLMFactory.create_llm(llm_provider, params, **kwargs)
    except Exception as e:
        st.error(f"Error creating LLM: {str(e)}")
        st.stop()


def get_response(prompt: str, llm_provider: str):
    """Get a response from the LLM using Streamlit session state."""
    try:
        params = st.session_state.get('params', {})
        return LLMFactory.get_response(prompt, llm_provider, params)
    except Exception as e:
        return f"Error during LLM invocation: {str(e)}"


def get_response_stream(
    prompt: str,
    llm_provider: str,
    system: Optional[str] = '',
    temperature: float = 0.9,
    max_tokens: int = 30000,
    **kwargs,
):
    """
    Get a streaming response from the LLM using Streamlit session state.
    """
    try:
        params = st.session_state.get('params', {})
        
        return LLMFactory.get_response_stream(
            prompt=prompt,
            llm_provider=llm_provider,
            config=params,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    except Exception as e:
        st.error(f"[Error during streaming: {str(e)}]")
        st.stop() 
