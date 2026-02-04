#!/usr/bin/env python3
"""
Test script for Voxies Slack Bot
Run this to verify your setup before deploying
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_agent():
    """Test the core agent functionality"""
    print("🧪 Testing App Agent...")
    
    try:
        from core_agent import SlackAppAgent
        
        # Initialize agent
        agent = SlackAppAgent()
        await agent.initialize()
        
        # Test query
        print("🔍 Testing query: 'What data do you have access to?'")
        response = await agent.process_query("What data do you have access to?")
        
        print("✅ Agent Response:")
        print(response)
        print()
        
        # Cleanup
        await agent.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")
    
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER", 
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_ROLE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
        "OPENAI_API_KEY"
    ]
    
    slack_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN"
    ]
    
    missing_required = []
    missing_slack = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}: Set")
    
    for var in slack_vars:
        if not os.getenv(var):
            missing_slack.append(var)
        else:
            print(f"✅ {var}: Set")
    
    if missing_required:
        print(f"❌ Missing required variables: {', '.join(missing_required)}")
        return False
    
    if missing_slack:
        print(f"⚠️  Missing Slack variables: {', '.join(missing_slack)}")
        print("   Slack bot won't work without these!")
        return False
    
    print("✅ All environment variables are set!")
    return True

def test_imports():
    """Test that all required imports work"""
    print("📦 Testing Imports...")
    
    try:
        import slack_bolt
        print("✅ slack-bolt imported")
        
        import langchain
        print("✅ langchain imported")
        
        import langchain_mcp_adapters
        print("✅ langchain-mcp-adapters imported")
        
        import langgraph
        print("✅ langgraph imported")
        
        # Test client imports
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))
        
        from services.streamlit_ai_service import create_llm_model
        print("✅ streamlit_ai_service imported")
        
        from utils.ai_prompts import make_system_prompt
        print("✅ ai_prompts imported")
        
        from config import DEFAULT_MAX_ITERATIONS
        print("✅ config imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Voxies Slack Bot Test Suite")
    print("=" * 40)
    
    # Test 1: Environment
    env_ok = test_environment()
    print()
    
    # Test 2: Imports
    imports_ok = test_imports()
    print()
    
    # Test 3: Agent (only if env and imports are OK)
    agent_ok = False
    if env_ok and imports_ok:
        agent_ok = await test_agent()
    else:
        print("⏭️  Skipping agent test due to previous failures")
    
    # Summary
    print("=" * 40)
    print("📋 Test Summary:")
    print(f"   Environment: {'✅' if env_ok else '❌'}")
    print(f"   Imports: {'✅' if imports_ok else '❌'}")
    print(f"   Agent: {'✅' if agent_ok else '❌'}")
    
    if env_ok and imports_ok and agent_ok:
        print("\n🎉 All tests passed! Your Slack bot is ready to deploy.")
        print("\n🚀 Next steps:")
        print("   1. Set up your Slack app (see README.md)")
        print("   2. Deploy with: docker compose up slack-bot --build -d")
        print("   3. Test in Slack with: @VoxiesBot hello")
    else:
        print("\n❌ Some tests failed. Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
