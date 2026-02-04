# Voxies Data Analytics Platform

AI-powered analytics for the Voxies ecosystem with a Streamlit UI, Slack bot, and MCP-based Snowflake access.

![Voxies Analytics](assets/main_connected.png)

## Features
- Streamlit chat UI for natural language analytics
- Slack bot for quick queries
- MCP server integration for Snowflake data access
- AppAgent shared across interfaces for consistent behavior
- Built-in logging and basic test runner

## Quick Start

### 1. Install Dependencies
```bash
python -m pip install -r agents/requirements.txt
python -m pip install -r client/requirements.txt
python -m pip install -r slack_bot/requirements.txt
```

### 2. Configure Environment
```bash
cp env.template .env
```

Required variables in `.env`:
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_ROLE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`
- `OPENAI_API_KEY`
- `STREAMLIT_API_KEY`

Optional (Slack):
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `ALLOWED_DOMAIN`

### 3. Run the Streamlit App
```bash
cd client
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

### 4. Run the Slack Bot (Optional)
```bash
python slack_bot/bot.py
```

## Tests
```bash
python run_tests.py
```

Note: tests require environment variables and external services to be configured.

## Project Structure
```
agents/              # AppAgent, MCP client, prompts, and LLM factory
client/              # Streamlit UI
slack_bot/           # Slack bot integration
servers/             # MCP server Docker setup
utils/               # Logging utilities
```

## Notes
- `.env` must be present at the repo root for local development.
- Do not commit secrets. Use `env.template` as a starting point.

