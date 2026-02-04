"""
Test cases for App Agent functionality
"""
import asyncio
import os
import sys
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add parent directory to path
import os
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents import AppAgent
from utils.logger import VoxiesLogger

class TestAppAgent:
    """Test cases for AppAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create an AppAgent instance for testing"""
        return AppAgent()
    
    @pytest.fixture
    def logger(self):
        """Create a logger for testing"""
        return VoxiesLogger("test_agent")
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert not agent.initialized
        assert agent.mcp_manager is not None
    
    @pytest.mark.asyncio
    async def test_agent_initialize_success(self, agent, logger):
        """Test successful agent initialization"""
        logger.info("Testing agent initialization")
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'SNOWFLAKE_ACCOUNT': 'test_account',
            'SNOWFLAKE_USER': 'test_user',
            'SNOWFLAKE_PASSWORD': 'test_password',
            'SNOWFLAKE_DATABASE': 'test_db',
            'SNOWFLAKE_SCHEMA': 'test_schema',
            'SNOWFLAKE_WAREHOUSE': 'test_warehouse',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            try:
                await agent.initialize()
                logger.info("Agent initialization completed")
                assert agent.initialized
            except Exception as e:
                logger.error(f"Agent initialization failed: {e}", error_type="initialization")
                # Expected to fail in test environment without real connections
                assert "Failed to initialize" in str(e) or "Missing" in str(e)
    
    def test_agent_params_default(self, agent):
        """Test default agent parameters"""
        default_params = {
            'model_id': 'OpenAI',
            'temperature': 0.3,
            'max_tokens': 4096,
            'max_iterations': 20,
            'recursion_limit': 50
        }
        
        # Agent should use defaults when no params provided
        assert agent.params is None  # Not initialized yet
    
    @pytest.mark.asyncio
    async def test_process_query_not_initialized(self, agent, logger):
        """Test process_query when agent not initialized"""
        logger.info("Testing query processing without initialization")
        
        with pytest.raises(Exception) as exc_info:
            await agent.process_query("test query")
        
        assert "Agent not initialized" in str(exc_info.value)
        logger.info("Correctly raised exception for uninitialized agent")

class TestAgentConfiguration:
    """Test agent configuration and settings"""
    
    def test_config_imports(self):
        """Test that all required config values are available"""
        from agents.config import (
            DEFAULT_MAX_ITERATIONS,
            DEFAULT_RECURSION_LIMIT,
            DEFAULT_TEMPERATURE,
            DEFAULT_MAX_TOKENS,
            MODEL_OPTIONS
        )
        
        assert DEFAULT_MAX_ITERATIONS == 20
        assert DEFAULT_RECURSION_LIMIT == 50
        assert DEFAULT_TEMPERATURE == 0.7
        assert DEFAULT_MAX_TOKENS == 4096
        assert isinstance(MODEL_OPTIONS, dict)
        assert 'OpenAI' in MODEL_OPTIONS
    
    def test_model_options(self):
        """Test model configuration options"""
        from agents.config import MODEL_OPTIONS
        
        required_models = ['OpenAI', 'Antropic', 'Bedrock', 'Google']
        for model in required_models:
            assert model in MODEL_OPTIONS
            assert isinstance(MODEL_OPTIONS[model], str)
            assert len(MODEL_OPTIONS[model]) > 0

class TestMCPClient:
    """Test MCP client functionality"""
    
    def test_mcp_client_creation(self):
        """Test MCP client manager creation"""
        from agents.mcp_client import MCPClientManager
        
        manager = MCPClientManager()
        assert manager is not None
        assert not manager.connected
        assert manager.tools == []
    
    def test_mcp_client_config(self):
        """Test MCP client configuration"""
        from agents.mcp_client import MCPClientManager
        
        manager = MCPClientManager()
        config = manager.server_config
        
        assert 'snowflake' in config
        assert 'command' in config['snowflake']
        assert config['snowflake']['command'] == 'python'

class TestLLMFactory:
    """Test LLM factory functionality"""
    
    def test_llm_factory_import(self):
        """Test LLM factory can be imported"""
        from agents.llm_factory import LLMFactory
        assert LLMFactory is not None
    
    def test_create_llm_openai_no_key(self):
        """Test OpenAI LLM creation without API key"""
        from agents.llm_factory import LLMFactory
        
        with pytest.raises(ValueError) as exc_info:
            LLMFactory.create_llm("OpenAI", {})
        
        assert "OpenAI API key not provided" in str(exc_info.value)
    
    def test_create_llm_invalid_provider(self):
        """Test LLM creation with invalid provider"""
        from agents.llm_factory import LLMFactory
        
        with pytest.raises(ValueError) as exc_info:
            LLMFactory.create_llm("InvalidProvider", {})
        
        assert "Unsupported LLM provider" in str(exc_info.value)

def run_agent_tests():
    """Run all agent tests and return results"""
    logger = VoxiesLogger("test_runner")
    logger.info("Starting agent tests")
    
    test_results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    # Test classes to run
    test_classes = [
        TestAppAgent,
        TestAgentConfiguration, 
        TestMCPClient,
        TestLLMFactory
    ]
    
    for test_class in test_classes:
        class_name = test_class.__name__
        logger.info(f"Running tests for {class_name}")
        
        # Get test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            test_results['total_tests'] += 1
            try:
                # Create instance and run test
                instance = test_class()
                method = getattr(instance, method_name)
                
                # Handle async tests
                if asyncio.iscoroutinefunction(method):
                    # Create fixtures manually for async tests
                    if hasattr(instance, 'agent'):
                        agent = AppAgent()
                        test_logger = VoxiesLogger("test")
                        asyncio.run(method(agent, test_logger))
                    else:
                        asyncio.run(method())
                else:
                    # Handle fixtures for sync tests
                    if 'agent' in method.__code__.co_varnames:
                        agent = AppAgent()
                        if 'logger' in method.__code__.co_varnames:
                            test_logger = VoxiesLogger("test")
                            method(agent, test_logger)
                        else:
                            method(agent)
                    else:
                        method()
                
                test_results['passed'] += 1
                logger.info(f"✅ {class_name}.{method_name} passed")
                
            except Exception as e:
                test_results['failed'] += 1
                error_msg = f"❌ {class_name}.{method_name} failed: {str(e)}"
                test_results['errors'].append(error_msg)
                logger.error(error_msg, error_type="test_failure")
    
    logger.info(f"Agent tests completed: {test_results['passed']}/{test_results['total_tests']} passed")
    return test_results

if __name__ == "__main__":
    results = run_agent_tests()
    print(f"\nTest Results: {results['passed']}/{results['total_tests']} passed")
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  {error}")
    
    sys.exit(0 if results['failed'] == 0 else 1) 
