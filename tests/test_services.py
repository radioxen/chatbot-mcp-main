"""
Test cases for App Services (Streamlit and Slack bot)
"""
import asyncio
import os
import sys
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add parent directory to path
import os
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logger import VoxiesLogger

class TestStreamlitService:
    """Test cases for Streamlit service"""
    
    def test_streamlit_imports(self):
        """Test that Streamlit service modules can be imported"""
        logger = VoxiesLogger("test_streamlit")
        logger.info("Testing Streamlit imports")
        
        try:
            from client.services.streamlit_agent import StreamlitAppAgent
            from client.services.streamlit_ai_service import create_llm_model
            logger.info("✅ Streamlit imports successful")
            return True
        except ImportError as e:
            logger.error(f"Streamlit import failed: {e}", error_type="import_error")
            return False
    
    def test_streamlit_agent_creation(self):
        """Test Streamlit agent creation"""
        logger = VoxiesLogger("test_streamlit")
        logger.info("Testing Streamlit agent creation")
        
        try:
            from client.services.streamlit_agent import StreamlitAppAgent
            agent = StreamlitAppAgent()
            assert agent is not None
            logger.info("✅ Streamlit agent created successfully")
            return True
        except Exception as e:
            logger.error(f"Streamlit agent creation failed: {e}", error_type="creation_error")
            return False
    
    def test_streamlit_config(self):
        """Test Streamlit configuration"""
        logger = VoxiesLogger("test_streamlit")
        logger.info("Testing Streamlit configuration")
        
        try:
            # Check if required files exist
            config_files = [
                'client/app.py',
                'client/.streamlit/config.toml',
                'client/requirements.txt'
            ]
            
            for file_path in config_files:
                if not os.path.exists(file_path):
                    logger.error(f"Missing config file: {file_path}", error_type="config_error")
                    return False
            
            logger.info("✅ Streamlit configuration files present")
            return True
        except Exception as e:
            logger.error(f"Streamlit config check failed: {e}", error_type="config_error")
            return False

class TestSlackBotService:
    """Test cases for Slack bot service"""
    
    def test_slack_bot_imports(self):
        """Test that Slack bot modules can be imported"""
        logger = VoxiesLogger("test_slack")
        logger.info("Testing Slack bot imports")
        
        try:
            from slack_bot.core_agent import SlackAppAgent
            from slack_bot.bot import app  # Slack Bolt app
            logger.info("✅ Slack bot imports successful")
            return True
        except ImportError as e:
            logger.error(f"Slack bot import failed: {e}", error_type="import_error")
            return False
    
    def test_slack_agent_creation(self):
        """Test Slack agent creation"""
        logger = VoxiesLogger("test_slack")
        logger.info("Testing Slack agent creation")
        
        try:
            from slack_bot.core_agent import SlackAppAgent
            agent = SlackAppAgent()
            assert agent is not None
            logger.info("✅ Slack agent created successfully")
            return True
        except Exception as e:
            logger.error(f"Slack agent creation failed: {e}", error_type="creation_error")
            return False
    
    def test_slack_config(self):
        """Test Slack bot configuration"""
        logger = VoxiesLogger("test_slack")
        logger.info("Testing Slack bot configuration")
        
        try:
            # Check if required files exist
            config_files = [
                'slack_bot/bot.py',
                'slack_bot/core_agent.py',
                'slack_bot/requirements.txt'
            ]
            
            for file_path in config_files:
                if not os.path.exists(file_path):
                    logger.error(f"Missing config file: {file_path}", error_type="config_error")
                    return False
            
            logger.info("✅ Slack bot configuration files present")
            return True
        except Exception as e:
            logger.error(f"Slack config check failed: {e}", error_type="config_error")
            return False

class TestEnvironmentSetup:
    """Test environment setup and configuration"""
    
    def test_environment_template(self):
        """Test environment template exists"""
        logger = VoxiesLogger("test_env")
        logger.info("Testing environment template")
        
        if not os.path.exists('env.template'):
            logger.error("env.template file missing", error_type="config_error")
            return False
        
        # Check template has required variables
        with open('env.template', 'r') as f:
            content = f.read()
            
        required_vars = [
            'SNOWFLAKE_ACCOUNT',
            'SNOWFLAKE_USER',
            'SNOWFLAKE_PASSWORD',
            'OPENAI_API_KEY',
            'SLACK_BOT_TOKEN'
        ]
        
        for var in required_vars:
            if var not in content:
                logger.error(f"Missing environment variable in template: {var}", error_type="config_error")
                return False
        
        logger.info("✅ Environment template valid")
        return True
    
    def test_logging_setup(self):
        """Test logging system setup"""
        logger = VoxiesLogger("test_logging")
        logger.info("Testing logging system")
        
        try:
            # Test logging functionality
            logger.debug("Debug message test")
            logger.info("Info message test")
            logger.warning("Warning message test")
            
            # Check if log files are created
            log_files = [
                'logs/test_logging_operations.csv',
                'logs/test_logging_errors.csv',
                'logs/test_logging_performance.csv'
            ]
            
            for log_file in log_files:
                if not os.path.exists(log_file):
                    logger.error(f"Log file not created: {log_file}", error_type="logging_error")
                    return False
            
            logger.info("✅ Logging system working")
            return True
        except Exception as e:
            logger.error(f"Logging test failed: {e}", error_type="logging_error")
            return False

class TestIntegration:
    """Integration tests for complete system"""
    
    def test_agent_integration(self):
        """Test agent integration between services"""
        logger = VoxiesLogger("test_integration")
        logger.info("Testing agent integration")
        
        try:
            # Test that both services can import the shared agent
            from agents import AppAgent
            from client.services.streamlit_agent import StreamlitAppAgent
            from slack_bot.core_agent import SlackAppAgent
            
            # Create instances
            base_agent = AppAgent()
            streamlit_agent = StreamlitAppAgent()
            slack_agent = SlackAppAgent()
            
            assert base_agent is not None
            assert streamlit_agent is not None
            assert slack_agent is not None
            
            logger.info("✅ Agent integration successful")
            return True
        except Exception as e:
            logger.error(f"Agent integration failed: {e}", error_type="integration_error")
            return False
    
    def test_dependency_compatibility(self):
        """Test that all dependencies are compatible"""
        logger = VoxiesLogger("test_deps")
        logger.info("Testing dependency compatibility")
        
        try:
            # Test key imports
            import langchain
            import openai
            import streamlit
            import slack_bolt
            
            logger.info("✅ Dependencies compatible")
            return True
        except ImportError as e:
            logger.error(f"Dependency incompatibility: {e}", error_type="dependency_error")
            return False

def run_service_tests():
    """Run all service tests and return results"""
    logger = VoxiesLogger("test_runner")
    logger.info("Starting service tests")
    
    test_results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    # Test classes to run
    test_classes = [
        TestStreamlitService,
        TestSlackBotService,
        TestEnvironmentSetup,
        TestIntegration
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
                result = method()
                
                if result:
                    test_results['passed'] += 1
                    logger.info(f"✅ {class_name}.{method_name} passed")
                else:
                    test_results['failed'] += 1
                    error_msg = f"❌ {class_name}.{method_name} failed"
                    test_results['errors'].append(error_msg)
                    logger.error(error_msg, error_type="test_failure")
                
            except Exception as e:
                test_results['failed'] += 1
                error_msg = f"❌ {class_name}.{method_name} failed: {str(e)}"
                test_results['errors'].append(error_msg)
                logger.error(error_msg, error_type="test_failure")
    
    logger.info(f"Service tests completed: {test_results['passed']}/{test_results['total_tests']} passed")
    return test_results

if __name__ == "__main__":
    results = run_service_tests()
    print(f"\nTest Results: {results['passed']}/{results['total_tests']} passed")
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  {error}")
    
    sys.exit(0 if results['failed'] == 0 else 1) 
