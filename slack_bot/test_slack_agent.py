#!/usr/bin/env python3
"""
Test script to verify the SlackAppAgent works correctly with the updated AppAgent.
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core_agent import SlackAppAgent

async def test_slack_agent():
    print("🧪 Testing SlackAppAgent with updated AppAgent...")
    
    # Create Slack agent
    slack_agent = SlackAppAgent()
    
    try:
        # Initialize agent
        print("📡 Initializing Slack agent...")
        await slack_agent.initialize()
        print("✅ Slack agent initialized successfully")
        
        # Test query
        print("\n🔍 Testing query: 'How many voxie classes are there?'")
        response = await slack_agent.process_query("How many voxie classes are there?")
        
        print(f"\n📱 Slack Response:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        
        # Test another query
        print("\n🔍 Testing query: 'What are the different voxie classes?'")
        response2 = await slack_agent.process_query("What are the different voxie classes?")
        
        print(f"\n📱 Slack Response 2:")
        print("=" * 50)
        print(response2)
        print("=" * 50)
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        await slack_agent.cleanup()

if __name__ == "__main__":
    # Check if required environment variables are set
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
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all variables are set.")
        sys.exit(1)
    
    asyncio.run(test_slack_agent()) 
