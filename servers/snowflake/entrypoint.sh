#!/bin/bash

# Convert environment variables to command line arguments
exec mcp_snowflake_server \
  --account "$SNOWFLAKE_ACCOUNT" \
  --user "$SNOWFLAKE_USER" \
  --password "$SNOWFLAKE_PASSWORD" \
  --role "$SNOWFLAKE_ROLE" \
  --warehouse "$SNOWFLAKE_WAREHOUSE" \
  --database "$SNOWFLAKE_DATABASE" \
  --schema "$SNOWFLAKE_SCHEMA" \
  --host "0.0.0.0" \
  --port "8100" \
  --transport "sse" 