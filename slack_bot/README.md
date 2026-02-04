# Voxies Slack Bot 🎮💬

Slack integration for the Voxies Data Analytics Agent. Reuses the exact same React agent and MCP Snowflake server as the Streamlit application.

## 🎯 Features

- **Same Intelligence** - Uses identical React agent logic as Streamlit app
- **Domain Restriction** - Only `@alwaysgeekygames.com` users can access
- **Multiple Interfaces** - Mentions, slash commands, and DMs
- **Thread Responses** - Keeps channels clean with threaded replies
- **Real-time Data** - Direct access to Snowflake via MCP server

## 🚀 Quick Start

### 1. Slack App Setup

**Create Slack App:**
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Voxies Analytics Bot"
4. Choose your workspace

**Configure OAuth Scopes:**
Add these Bot Token Scopes:
```
app_mentions:read    # Read mentions
channels:read        # Read channel info
chat:write          # Send messages
commands            # Slash commands
im:read             # Read DMs
im:write            # Send DMs
users:read          # Read user profiles
users:read.email    # Read user emails (for domain verification)
```

**Enable Socket Mode:**
1. Go to "Socket Mode" in your app settings
2. Enable Socket Mode
3. Generate App-Level Token with `connections:write` scope
4. Save the token (starts with `xapp-`)

**Create Slash Command:**
1. Go to "Slash Commands"
2. Create command: `/voxies`
3. Request URL: `http://localhost:3000/slack/events` (placeholder)
4. Description: "Ask Voxies analytics questions"

**Enable Events:**
1. Go to "Event Subscriptions"
2. Enable Events
3. Subscribe to Bot Events:
   - `app_mention`
   - `message.im`

**Install to Workspace:**
1. Go to "Install App"
2. Install to your workspace
3. Copy the Bot User OAuth Token (starts with `xoxb-`)

### 2. Environment Configuration

**Add to your main `.env` file:**
```bash
# Slack Bot Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
ALLOWED_DOMAIN=alwaysgeekygames.com

# Your existing Snowflake and OpenAI config stays the same
```

### 3. Deploy

**Option A: With Streamlit (Recommended)**
```bash
# Deploy both Streamlit and Slack bot
docker compose up --build -d

# View logs
docker compose logs -f slack-bot
```

**Option B: Slack Bot Only**
```bash
# Deploy just the Slack bot
docker compose up slack-bot --build -d
```

## 💬 Usage

### Mention in Channels
```
@VoxiesBot How many battles happened yesterday?
@VoxiesBot Show me token rewards for last week
@VoxiesBot What are the top player statistics?
```

### Slash Commands
```
/voxies How many active players today?
/voxies Show marketplace sales trends
/voxies What's the battle win rate by player level?
```

### Direct Messages
```
Just message the bot directly:
"What data do you have access to?"
"Can you show me recent player activity?"
```

## 🔒 Security

- **Domain Restriction** - Only `@alwaysgeekygames.com` emails can use the bot
- **User Verification** - Checks user email on every request
- **Thread Responses** - Keeps sensitive data in threads
- **Same MCP Security** - Inherits all Snowflake access controls

## 🛠️ Architecture

```
Slack User → Slack Bot → Core Agent → MCP Client → MCP Snowflake Server → Snowflake
```

**Shared Components:**
- `core_agent.py` - Reuses exact Streamlit agent logic
- `client/services/` - AI service, MCP service (shared)
- `client/utils/` - Prompts, async helpers (shared)
- `snowflake_launcher.py` - MCP server launcher (shared)

## 📊 Example Conversations

**Channel Mention:**
```
User: @VoxiesBot How many tokens did we reward players in June?
Bot: 📊 Analysis completed using 3 data queries

Based on the latest data from VOXIES.ANALYTICS.BATTLE_TOKEN_REWARDS:

Total tokens rewarded in June 2024: 2,847,392 tokens
- Average per day: 94,913 tokens
- Peak day: June 15th with 156,203 tokens
- Total unique players rewarded: 1,247 players
```

**Slash Command:**
```
User: /voxies What are the top 5 most active players?
Bot: 🎮 Voxies Analytics Results:

Top 5 Most Active Players (Last 30 Days):
1. Player_7A2B: 847 battles, 2.1M tokens earned
2. Player_9C4D: 723 battles, 1.8M tokens earned
3. Player_5E6F: 692 battles, 1.7M tokens earned
4. Player_1G8H: 634 battles, 1.5M tokens earned
5. Player_3I0J: 598 battles, 1.4M tokens earned
```

## 🔧 Troubleshooting

**Bot not responding:**
```bash
# Check logs
docker compose logs slack-bot

# Restart bot
docker compose restart slack-bot
```

**Permission errors:**
- Verify OAuth scopes are correctly set
- Check that Socket Mode is enabled
- Ensure bot is added to channels where you're testing

**Domain restriction issues:**
- Verify users have `@alwaysgeekygames.com` emails in Slack profiles
- Check `ALLOWED_DOMAIN` environment variable

**MCP connection issues:**
- Ensure Snowflake credentials are correct
- Check that MCP server can connect to Snowflake
- Verify shared volumes are mounted correctly

## 📝 Development

**Local Testing:**
```bash
# Run locally with your .env
cd slack_bot
pip install -r requirements.txt
python bot.py
```

**Adding New Features:**
- Modify `core_agent.py` for agent logic changes
- Update `bot.py` for Slack-specific features
- Changes to prompts/services affect both Streamlit and Slack

## 🔄 Updates

The Slack bot automatically inherits updates to:
- AI prompts and system messages
- MCP server improvements
- Snowflake query optimizations
- React agent enhancements

Just rebuild and redeploy:
```bash
docker compose up --build -d
``` 