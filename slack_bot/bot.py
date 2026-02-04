"""
Voxies Slack Bot - Integrates with existing MCP Snowflake agent
"""
import asyncio
import os
import signal
import sys
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from dotenv import load_dotenv
import nest_asyncio

# Enable nested event loops for compatibility
nest_asyncio.apply()

from core_agent import SlackAppAgent

# Load environment variables
load_dotenv()

# Validate required environment variables
required_env_vars = [
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN", 
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_DATABASE", 
    "SNOWFLAKE_SCHEMA",
    "OPENAI_API_KEY"
]

missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file and ensure all variables are set.")
    sys.exit(1)

# Initialize Slack app
app = AsyncApp(token=os.environ.get("SLACK_BOT_TOKEN"))

# Initialize app agent (reusing exact same logic as Streamlit)
app_agent = SlackAppAgent()

# Company domain restriction (load from env with fallback)
ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN", "alwaysgeekygames.com")

def is_authorized_user(user_id: str) -> bool:
    """Check if user is authorized - for internal org, all workspace users are allowed"""
    return True

async def get_user_info(client, user_id: str) -> dict:
    """Get user info from Slack API"""
    try:
        response = await client.users_info(user=user_id)
        return {
            "name": response["user"].get("name", "unknown"),
            "real_name": response["user"]["profile"].get("real_name", "")
        }
    except Exception as e:
        print(f"Error getting user info: {e}")
        return {"name": "unknown", "real_name": ""}

@app.event("app_mention")
async def handle_mention(event, say, client):
    """Handle @VoxiesBot mentions in channels - respond via DM"""
    user_id = event.get("user")
    channel_id = event.get("channel")
    
    # Check authorization
    user_info = await get_user_info(client, user_id)
    if not is_authorized_user(user_id):
        # Send authorization error as DM
        try:
            await client.chat_postMessage(
                channel=user_id,  # Send DM to user
                text="🚫 Access denied. This bot is for internal use only."
            )
        except Exception:
            # Fallback to channel if DM fails
            await client.chat_postMessage(
                channel=channel_id,
                text="🚫 Access denied. This bot is for internal use only."
            )
        return
    
    # Extract message (remove bot mention)
    bot_user_id = (await client.auth_test())["user_id"]
    user_message = event['text'].replace(f"<@{bot_user_id}>", "").strip()
    
    if not user_message:
        # Send help message as DM
        try:
            await client.chat_postMessage(
                channel=user_id,  # Send DM to user
                text="🧙‍♂️ Greetings! I'm Elder Voxie, your magical data wizard! ✨\n\nI can help you discover insights about:\n• 🎮 Game analytics & player data\n• ⚔️ Battle statistics & performance\n• 🪙 Token rewards & distribution\n• 📊 Player behavior & trends\n\nExample: *'How many battles happened yesterday?'* or *'Show me token rewards this week'*"
            )
            # Also acknowledge in channel that we sent a DM
            await client.chat_postMessage(
                channel=channel_id,
                text=f"👋 <@{user_id}> I've sent you a DM with instructions!"
            )
        except Exception:
            # Fallback to channel if DM fails
            await client.chat_postMessage(
                channel=channel_id,
                text="🧙‍♂️ Greetings! I'm Elder Voxie, your magical data wizard! ✨\n\nAsk me about game analytics, battles, token rewards, and player data!\n\nExample: `@VoxiesBot How many battles happened yesterday?`"
            )
        return
    
    try:
        # Send Elder Voxie processing message as DM
        await client.chat_postMessage(
            channel=user_id,  # Send DM to user
            text="🔮 Elder Voxie is analyzing your query...\n✨ *Casting spells on the Voxies database* ✨"
        )
        
        # Also acknowledge in channel that we're processing via DM
        await client.chat_postMessage(
            channel=channel_id,
            text=f"🔮 <@{user_id}> Elder Voxie is processing your question via DM... ✨"
        )
        
        # Process with Voxies agent
        response = await app_agent.process_query(user_message)
        
        # Send response as DM with Elder Voxie branding
        await client.chat_postMessage(
            channel=user_id,  # Send DM to user
            text=f"🧙‍♂️ **Elder Voxie's Analytics Results:**\n\n{response}\n\n✨ *Data magic complete!* ✨"
        )
        
    except Exception as e:
        # Send error as DM
        try:
            await client.chat_postMessage(
                channel=user_id,  # Send DM to user
                text=f"❌ Error processing your request: {str(e)}\n\nPlease try again or contact support."
            )
        except Exception:
            # Fallback to channel if DM fails
            await client.chat_postMessage(
                channel=channel_id,
                text=f"❌ <@{user_id}> Error processing your request. Please try DMing me directly."
            )
        print(f"Error in handle_mention: {e}")

@app.command("/voxies")
async def handle_voxies_command(ack, respond, command, client):
    """Handle /voxies slash command - respond via DM"""
    await ack()
    
    user_id = command.get("user_id")
    channel_id = command.get("channel_id")
    
    # Check authorization
    user_info = await get_user_info(client, user_id)
    if not is_authorized_user(user_id):
        await respond("🚫 Access denied. This bot is for internal use only.")
        return
    
    query = command.get('text', '').strip()
    
    if not query:
        await respond({
            "response_type": "ephemeral",
            "text": "🧙‍♂️ **Elder Voxie - Data Wizard** ✨\n\nUsage: `/voxies <your question>`\n\nExamples:\n• `/voxies How many active players today?`\n• `/voxies Show token rewards for last week`\n• `/voxies What are the top battle statistics?`\n• `/voxies Which Voxie classes are most popular?`\n\n💡 **Tip**: I'll send my magical analysis via DM to keep the channel clean!"
        })
        return
    
    try:
        # Send immediate acknowledgment in channel
        await respond({
            "response_type": "in_channel",
            "text": f"🔮 Elder Voxie is processing your question via DM... ✨"
        })
        
        # Send processing message as DM
        await client.chat_postMessage(
            channel=user_id,  # Send DM to user
            text="🔮 Elder Voxie is analyzing your query...\n✨ *Casting spells on the Voxies database* ✨"
        )
        
        # Process with Voxies agent
        response = await app_agent.process_query(query)
        
        # Send response as DM with Elder Voxie branding
        await client.chat_postMessage(
            channel=user_id,  # Send DM to user
            text=f"🧙‍♂️ **Elder Voxie's Analytics Results:**\n\n{response}\n\n✨ *Data magic complete!* ✨"
        )
        
    except Exception as e:
        # Send error as DM
        try:
            await client.chat_postMessage(
                channel=user_id,  # Send DM to user
                text=f"❌ Error processing your request: {str(e)}\n\nPlease try again or contact support."
            )
        except Exception:
            # Fallback to channel if DM fails
            await client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Error processing your request. Please try DMing me directly."
            )
        print(f"Error in handle_voxies_command: {e}")

@app.event("message")
async def handle_direct_message(event, say, client):
    """Handle direct messages to the bot"""
    # Skip if it's a bot message or in a channel
    if event.get('bot_id') or event.get('channel_type') != 'im':
        return
    
    user_id = event.get("user")
    
    # Check authorization
    user_info = await get_user_info(client, user_id)
    if not is_authorized_user(user_id):
        await say("🚫 Access denied. This bot is for internal use only.")
        return
    
    user_message = event.get('text', '').strip()
    
    if not user_message:
        return
    
    try:
        # Process with Voxies agent
        response = await app_agent.process_query(user_message)
        await say(f"🎮 **Voxies Analytics:**\n\n{response}")
        
    except Exception as e:
        await say(f"❌ Error: {str(e)}")
        print(f"Error in handle_direct_message: {e}")

async def main():
    """Main function to start the bot"""
    print("🚀 Starting Voxies Slack Bot...")
    
    # Initialize the Voxies agent
    try:
        await app_agent.initialize()
    except Exception as e:
        print(f"❌ Failed to initialize Voxies agent: {e}")
        sys.exit(1)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Shutting down Voxies Slack Bot...")
        asyncio.create_task(app_agent.cleanup())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Slack bot
    handler = AsyncSocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    
    print("✅ Voxies Slack Bot is running!")
    print(f"🔒 Authorized domain: @{ALLOWED_DOMAIN}")
    print("📝 Available commands:")
    print("   • @VoxiesBot <question> - Ask in any channel")
    print("   • /voxies <question> - Use slash command")
    print("   • Direct message the bot")
    
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main()) 
