#!/usr/bin/env python3
"""
Slack Bot Wrapper - Sets up imports and runs the bot
"""
import os
import sys
import asyncio

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import and run the bot
if __name__ == "__main__":
    try:
        # Import the bot module
        import bot
        print("🤖 Slack bot started successfully")
        
        # Actually run the bot's main function
        asyncio.run(bot.main())
        
    except Exception as e:
        print(f"❌ Failed to start Slack bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 