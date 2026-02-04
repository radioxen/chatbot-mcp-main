#!/usr/bin/env python
"""Launches mcp_snowflake_server with env-var credentials.

Run via: python snowflake_launcher.py
"""
import os
import sys
from dotenv import load_dotenv
import mcp_snowflake_server as mss

# Load environment variables from .env file
# Look for .env file in the project root (two levels up from agents/)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

REQ_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]

# Debug: Print all environment variables that start with SNOWFLAKE
print("DEBUG: Available SNOWFLAKE env vars:", file=sys.stderr)
for key, value in os.environ.items():
    if key.startswith("SNOWFLAKE_"):
        print(f"  {key}={value[:10]}..." if len(value) > 10 else f"  {key}={value}", file=sys.stderr)

missing = [v for v in REQ_VARS if v not in os.environ or not os.environ[v]]
if missing:
    print(f"DEBUG: Missing Snowflake env vars: {', '.join(missing)}", file=sys.stderr)
    print(f"DEBUG: Current working directory: {os.getcwd()}", file=sys.stderr)
    print(f"DEBUG: Python executable: {sys.executable}", file=sys.stderr)
    sys.stderr.write(f"Missing Snowflake env vars: {', '.join(missing)}\n")
    sys.exit(1)

print("DEBUG: All required env vars found, starting MCP server", file=sys.stderr)

if __name__ == "__main__":
    # Ensure program name for argparse; no additional CLI args as we rely on env vars
    sys.argv = ["mcp_snowflake_server"]
    mss.main() 