"""
Simplified Voxies Slack Bot - For Testing Slack Integration
"""
import asyncio
import os
import signal
import sys
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from dotenv import load_dotenv
import nest_asyncio
import json
from datetime import datetime

# Enable nested event loops for compatibility
nest_asyncio.apply()

# Load environment variables
load_dotenv('../.env')

# Validate required environment variables
required_env_vars = [
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN", 
    "OPENAI_API_KEY"
]

missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file and ensure all variables are set.")
    sys.exit(1)

# Initialize Slack app
app = AsyncApp(token=os.environ.get("SLACK_BOT_TOKEN"))

# Company domain restriction (load from env with fallback)
ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN", "alwaysgeekygames.com")

def log_with_timestamp(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def is_authorized_user(user_id: str) -> bool:
    """Check if user is authorized - for internal org, all workspace users are allowed"""
    # For internal org app, all users in the workspace are authorized
    log_with_timestamp(f"🔒 Auth check: {user_id} -> ✅ (internal org - all users allowed)")
    return True

async def get_user_info(client, user_id: str) -> dict:
    """Get user info from Slack API"""
    try:
        response = await client.users_info(user=user_id)
        user_info = {
            "name": response["user"].get("name", "unknown"),
            "real_name": response["user"]["profile"].get("real_name", ""),
            "display_name": response["user"]["profile"].get("display_name", "")
        }
        log_with_timestamp(f"👤 User {user_id}: {user_info['real_name']} (@{user_info['name']})")
        return user_info
    except Exception as e:
        log_with_timestamp(f"❌ Error getting user info for {user_id}: {e}")
        return {"name": "unknown", "real_name": "", "display_name": ""}

async def simple_voxies_response(user_message: str) -> str:
    """Simple response function - replace with actual agent later"""
    
    # Simple keyword-based responses for testing
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "👋 Hello! I'm the Voxies Data Agent. I can help you analyze game data, player statistics, token rewards, and battle analytics!\n\n*Note: Full analytics features coming soon - this is a connection test.*"
    
    elif any(word in message_lower for word in ['help', 'what', 'how']):
        return """🎮 **Voxies Analytics Bot**

I can help you with:
• 📊 Player statistics and analytics
• 💰 Token reward analysis  
• ⚔️ Battle data and performance
• 📈 Game metrics and trends

**Example questions:**
• "How many active players today?"
• "Show token rewards for last week"
• "What are the top battle statistics?"

*Full Snowflake integration coming online...*"""
    
    elif any(word in message_lower for word in ['player', 'user', 'active']):
        return "📊 **Player Analytics**\n\nI can analyze player data including:\n• Active player counts\n• Session durations\n• Level progression\n• Engagement metrics\n\n*Connecting to Snowflake database...*"
    
    elif any(word in message_lower for word in ['token', 'reward', 'earn']):
        return "💰 **Token & Rewards Analysis**\n\nI can track:\n• Token distribution\n• Reward calculations\n• Earning patterns\n• Economic metrics\n\n*Querying token database...*"
    
    elif any(word in message_lower for word in ['battle', 'fight', 'combat']):
        return "⚔️ **Battle Analytics**\n\nBattle data includes:\n• Win/loss ratios\n• Combat statistics\n• Performance metrics\n• Strategy analysis\n\n*Analyzing battle logs...*"
    
    else:
        return f"🤖 I received your message: '{user_message}'\n\n📊 I'm the Voxies analytics agent! I can help with game data analysis.\n\n*Full MCP Snowflake integration is being configured...*"

# Log ALL events for monitoring
@app.event({"type": "message"})
async def log_all_messages(event, say, client):
    """Log all message events and handle DMs"""
    log_with_timestamp(f"📨 MESSAGE: channel={event.get('channel')}, user={event.get('user')}, text='{event.get('text')}', channel_type={event.get('channel_type')}")
    
    # Handle direct messages
    if event.get('channel_type') == 'im' and not event.get('bot_id'):
        log_with_timestamp("🎯 Processing DIRECT MESSAGE")
        await handle_direct_message(event, say, client)

@app.event("app_mention")
async def handle_mention(event, say, client):
    """Handle @VoxiesBot mentions in channels"""
    log_with_timestamp(f"🎯 MENTION: channel={event.get('channel')}, user={event.get('user')}, text='{event.get('text')}'")
    
    user_id = event.get("user")
    
    # Check authorization (get user info for logging)
    user_info = await get_user_info(client, user_id)
    if not is_authorized_user(user_id):
        log_with_timestamp("🚫 User not authorized for mention")
        await say("🚫 Access denied. This bot is for internal use only.")
        return
    
    # Extract message (remove bot mention)
    bot_user_id = (await client.auth_test())["user_id"]
    user_message = event['text'].replace(f"<@{bot_user_id}>", "").strip()
    
    if not user_message:
        log_with_timestamp("📝 Empty mention - sending greeting")
        await say("👋 Hi! I'm the Voxies Data Agent. Ask me questions about game analytics, player data, token rewards, battles, and more!\n\nExample: `@VoxiesBot How many battles happened yesterday?`")
        return
    
    try:
        log_with_timestamp(f"🔍 Processing mention: '{user_message}'")
        
        # Show typing indicator
        await client.chat_postMessage(
            channel=event['channel'],
            text="🔍 Analyzing your query...",
            thread_ts=event.get('ts')
        )
        log_with_timestamp("✅ Typing indicator sent")
        
        # Process with simple response (replace with agent later)
        response = await simple_voxies_response(user_message)
        log_with_timestamp(f"📝 Generated response: {len(response)} chars")
        
        # Send response in thread to keep channel clean
        await say(
            text=f"🎮 **Voxies Analytics Results:**\n\n{response}",
            thread_ts=event.get('ts')
        )
        log_with_timestamp("✅ Mention response sent successfully")
        
    except Exception as e:
        log_with_timestamp(f"❌ Error in mention handler: {e}")
        await say(
            text=f"❌ Error processing your request: {str(e)}\n\nPlease try again or contact support.",
            thread_ts=event.get('ts')
        )

@app.command("/voxies")
async def handle_voxies_command(ack, respond, command, client):
    """Handle /voxies slash command"""
    log_with_timestamp(f"⚡ SLASH COMMAND: user={command.get('user_id')}, text='{command.get('text')}'")
    await ack()
    
    user_id = command.get("user_id")
    
    # Check authorization (get user info for logging)
    user_info = await get_user_info(client, user_id)
    if not is_authorized_user(user_id):
        log_with_timestamp("🚫 User not authorized for slash command")
        await respond("🚫 Access denied. This bot is for internal use only.")
        return
    
    query = command.get('text', '').strip()
    
    if not query:
        log_with_timestamp("📝 Empty slash command - sending help")
        await respond({
            "response_type": "ephemeral",
            "text": "🎮 **Voxies Data Agent**\n\nUsage: `/voxies <your question>`\n\nExamples:\n• `/voxies How many active players today?`\n• `/voxies Show token rewards for last week`\n• `/voxies What are the top battle statistics?`"
        })
        return
    
    try:
        log_with_timestamp(f"🔍 Processing slash command: '{query}'")
        
        # Send immediate response
        await respond({
            "response_type": "in_channel",
            "text": f"🔍 Analyzing: _{query}_"
        })
        log_with_timestamp("✅ Immediate slash response sent")
        
        # Process with simple response
        response = await simple_voxies_response(query)
        log_with_timestamp(f"📝 Generated slash response: {len(response)} chars")
        
        # Send follow-up response
        await client.chat_postMessage(
            channel=command['channel_id'],
            text=f"🎮 **Voxies Analytics Results:**\n\n{response}",
            thread_ts=command.get('ts')
        )
        log_with_timestamp("✅ Slash command follow-up sent successfully")
        
    except Exception as e:
        log_with_timestamp(f"❌ Error in slash command handler: {e}")
        await client.chat_postMessage(
            channel=command['channel_id'],
            text=f"❌ Error processing your request: {str(e)}\n\nPlease try again or contact support."
        )

async def handle_direct_message(event, say, client):
    """Handle direct messages to the bot"""
    user_id = event.get("user")
    user_message = event.get('text', '').strip()
    
    log_with_timestamp(f"🔍 Processing DM from {user_id}: '{user_message}'")
    
    # Check authorization (get user info for logging)
    user_info = await get_user_info(client, user_id)
    if not is_authorized_user(user_id):
        log_with_timestamp("🚫 User not authorized for DM")
        await say("🚫 Access denied. This bot is for internal use only.")
        return
    
    if not user_message:
        log_with_timestamp("⚠️ Empty DM - ignoring")
        return
    
    try:
        log_with_timestamp("📝 Generating DM response...")
        # Process with simple response
        response = await simple_voxies_response(user_message)
        log_with_timestamp(f"📝 Generated DM response: {len(response)} chars")
        
        await say(f"🎮 **Voxies Analytics:**\n\n{response}")
        log_with_timestamp("✅ DM response sent successfully")
        
    except Exception as e:
        log_with_timestamp(f"❌ Error in DM handler: {e}")
        await say(f"❌ Error: {str(e)}")

# Log connection events
@app.event("hello")
async def handle_hello(event):
    """Log connection events"""
    log_with_timestamp("👋 WebSocket connected!")

async def main():
    """Main function to start the bot"""
    log_with_timestamp("🚀 Starting Voxies Slack Bot (Simple Version with Monitoring)...")
    
    # Test authentication first
    try:
        auth_response = await app.client.auth_test()
        log_with_timestamp(f"✅ Authentication successful: {auth_response['user']} (ID: {auth_response['user_id']})")
    except Exception as e:
        log_with_timestamp(f"❌ Authentication failed: {e}")
        return
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        log_with_timestamp("🛑 Shutting down Voxies Slack Bot...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Slack bot
    handler = AsyncSocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    
    log_with_timestamp("✅ Voxies Slack Bot is running!")
    log_with_timestamp("🔒 Internal org app - all workspace users authorized")
    log_with_timestamp("📝 Available commands:")
    log_with_timestamp("   • @VoxiesBot <question> - Ask in any channel")
    log_with_timestamp("   • /voxies <question> - Use slash command")
    log_with_timestamp("   • Direct message the bot")
    log_with_timestamp("🔍 All events will be logged with timestamps")
    log_with_timestamp("📡 Waiting for Slack events...")
    
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main()) 