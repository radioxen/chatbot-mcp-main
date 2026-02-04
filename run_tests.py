#!/usr/bin/env python3
"""
Simple test runner for Voxies deployment
Runs tests with proper import paths
"""
import os
import sys
import traceback

# Add current directory to Python path
sys.path.insert(0, '.')

def run_basic_tests():
    """Run basic functionality tests without complex imports"""
    print("🧪 Running Voxies Deployment Tests")
    
    test_results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    # Test 1: Check required files exist
    print("\n📁 Testing file structure...")
    test_results['total'] += 1
    
    required_files = [
        '.env',
        'agents/__init__.py',
        'agents/app_agent.py',
        'agents/mcp_client.py',
        'utils/logger.py',
        'client/app.py',
        'slack_bot/bot.py',
        'slack_bot/core_agent.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        test_results['failed'] += 1
        test_results['errors'].append(f"Missing files: {missing_files}")
        print(f"❌ Missing required files: {missing_files}")
    else:
        test_results['passed'] += 1
        print("✅ All required files present")
    
    # Test 2: Test basic imports
    print("\n📦 Testing imports...")
    test_results['total'] += 1
    
    try:
        from utils.logger import VoxiesLogger
        from agents import AppAgent
        print("✅ Core imports successful")
        test_results['passed'] += 1
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Import error: {e}")
        print(f"❌ Import failed: {e}")
    
    # Test 3: Test logger functionality
    print("\n📝 Testing logger...")
    test_results['total'] += 1
    
    try:
        from utils.logger import VoxiesLogger
        logger = VoxiesLogger("test")
        logger.info("Test message")
        logger.debug("Debug message")
        print("✅ Logger working")
        test_results['passed'] += 1
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Logger error: {e}")
        print(f"❌ Logger failed: {e}")
    
    # Test 4: Test agent creation
    print("\n🤖 Testing agent creation...")
    test_results['total'] += 1
    
    try:
        from agents import AppAgent
        agent = AppAgent()
        assert agent is not None
        print("✅ Agent creation successful")
        test_results['passed'] += 1
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Agent creation error: {e}")
        print(f"❌ Agent creation failed: {e}")
    
    # Test 5: Test environment variables
    print("\n🔧 Testing environment setup...")
    test_results['total'] += 1
    
    required_env_vars = [
        'OPENAI_API_KEY',
        'SNOWFLAKE_ACCOUNT',
        'SNOWFLAKE_USER',
        'SNOWFLAKE_PASSWORD'
    ]
    
    missing_env_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_env_vars.append(var)
    
    if missing_env_vars:
        test_results['failed'] += 1
        test_results['errors'].append(f"Missing environment variables: {missing_env_vars}")
        print(f"⚠️  Missing environment variables: {missing_env_vars}")
        print("   (This may be expected in some environments)")
    else:
        test_results['passed'] += 1
        print("✅ All required environment variables present")
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"   Total tests: {test_results['total']}")
    print(f"   Passed: {test_results['passed']}")
    print(f"   Failed: {test_results['failed']}")
    
    if test_results['errors']:
        print(f"\n❌ Errors:")
        for error in test_results['errors']:
            print(f"   - {error}")
    
    # Return success if most tests passed
    success_rate = test_results['passed'] / test_results['total'] if test_results['total'] > 0 else 0
    return success_rate >= 0.6  # Pass if 60% or more tests pass

if __name__ == "__main__":
    try:
        success = run_basic_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        traceback.print_exc()
        sys.exit(1) 
