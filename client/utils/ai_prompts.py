import streamlit as st
import sys
import os

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents import TABLES

def make_system_prompt():
    """Create a comprehensive system prompt for the Voxies gaming data analytics agent"""
    
    # Organize use cases by category
    use_cases_by_category = {
        "Player Analytics": [],
        "Economic Analysis": [],
        "Game Performance": [],
        "NFT & Assets": [],
        "Technical Operations": []
    }
    
    # Categorize use cases from tables
    for table_name, info in TABLES.items():
        for use_case in info.get('use_cases', []):
            if any(keyword in use_case.lower() for keyword in ['player', 'user', 'retention', 'engagement', 'behavior']):
                use_cases_by_category["Player Analytics"].append(f"{table_name}: {use_case}")
            elif any(keyword in use_case.lower() for keyword in ['economic', 'revenue', 'token', 'reward', 'marketplace', 'transaction']):
                use_cases_by_category["Economic Analysis"].append(f"{table_name}: {use_case}")
            elif any(keyword in use_case.lower() for keyword in ['performance', 'battle', 'game', 'ranking', 'score']):
                use_cases_by_category["Game Performance"].append(f"{table_name}: {use_case}")
            elif any(keyword in use_case.lower() for keyword in ['nft', 'voxie', 'item', 'equipment', 'gear']):
                use_cases_by_category["NFT & Assets"].append(f"{table_name}: {use_case}")
            else:
                use_cases_by_category["Technical Operations"].append(f"{table_name}: {use_case}")
    
    # Generate organized use cases text
    use_cases_text = ""
    for category, cases in use_cases_by_category.items():
        if cases:
            use_cases_text += f"\n**{category}:**\n" + "\n".join(f"- {case}" for case in cases) + "\n"

    return f"""You are the **Voxies Snowflake Data Agent**.

GOAL
You are a SQL script writer expert and data analytics professional. 
Answer user questions with real data from the Voxies Snowflake warehouse accessed via MCP tools.
You are a SQL script writer expert and data analytics professional. 
The user question is always about the game data and the events happpened in the game.
The data you have access to is close to realtime.
Answer user questions with real data from the Voxies Snowflake warehouse accessed via MCP tools.

ALLOWED TOOLS
- snowflake_mcp • snowflake_mcp_server tool should always be used for answering questions
- list_databases • list_schemas • list_tables
- describe_table  – inspect table structure
- read_query      – run SELECT statements
- append_insight  – store discovered insights

WORKFLOW (use for EVERY question)
1. Always use your Snowflake MCP SERVER that you have to find the right table to query from.
2. Identify candidate tables.
3. ALWAYS call **describe_table** first to verify column names.
4. Build & run **read_query** (add filters, joins, aggregates) to fetch the answer.
5. Present findings grounded ONLY in query results; explain method and caveats.

TABLE USE-CASES
{use_cases_text}

Never make hallucinations. 
Never make up data. 

Keep replies concise, numeric, and evidence-based. Never invent data or skip the table-inspection step."""

def make_main_prompt(user_input: str) -> str:
    """Create the main prompt for user queries"""
    return f"""
**User Question:** {user_input}

**Instructions:**
1. Analyze this question to determine the best data approach
2. Identify relevant tables from your knowledge base
3. Use describe_table to verify table structures before querying
4. Extract real insights from the data warehouse
5. Provide a comprehensive, data-driven response
6. Include your verification checklist at the end

**Remember:** Ground every response in actual data. If you cannot find specific data, explain what's available and offer the closest relevant analysis.
"""