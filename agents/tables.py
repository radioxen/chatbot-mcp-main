"""
Voxies Gaming Data Warehouse - Table Structure Reference

This file contains data dictionaries for all key tables in the Voxies gaming data warehouse.
Each table entry includes:
- description: Brief explanation of what the table contains
- schema: Database schema (RAW or ANALYTICS)
- key_columns: Most important columns for analysis
- use_cases: Common analytical use cases for the table
"""

TABLES = {
    # ===== USER & PLAYER DATA =====
    "USER": {
        "description": "Master user table containing user registration, and basic profile information",
        "schema": "RAW",
        "key_columns": ["ID", "USERNAME", "WALLET", "CREATEDAT", "LASTLOGINAT", "BANNED", "WALLETTYPE"],
        "use_cases": ["User registration analysis", "Account status tracking", "Wallet integration analysis"]
    },
    
    "PLAYER_PROFILING": {
        "description": "Comprehensive player behavior and performance metrics including earnings, spending, and gameplay patterns",
        "schema": "ANALYTICS", 
        "key_columns": ["PLAYER", "DATE", "GAME_MODE", "BATTLE_COUNT", "WIN_RATE", "TOTAL_EARNING", "NET_EARNINGS", "TOTAL_TIME_PLAYED_MIN"],
        "use_cases": ["Player performance analysis", "Revenue per player", "Player engagement metrics", "Game balance analysis"]
    },
    
    # ===== BATTLE & GAMEPLAY DATA =====
    "DAILY_PLAYER_ACTIVITY_BY_GAMEMODE": {
        "description": "Daily player activity metrics broken down by game mode including battles, wins, losses, and time played",
        "schema": "ANALYTICS",
        "key_columns": ["PLAYER_ID", "DATE", "GAME_MODE", "BATTLES_COUNT", "WINS_COUNT", "LOSSES_COUNT", "HOURS_PLAYED", "PLAYER_RANKING"],
        "use_cases": ["Daily active users", "Game mode popularity", "Player performance tracking", "Engagement trends"]
    },
    
    "BATTLE_TOKEN_REWARDS": {
        "description": "Token rewards distributed to players after battles, including reward types, amounts, and player context, token_type.",
        "schema": "ANALYTICS",
        "key_columns": ["BATTLE_ID", "USER_ID", "USERNAME", "TOKENS_RECEIVED", "TOKEN_TYPE", "REWARD_TYPE", "GAME_MODE", "BATTLE_STATUS", "CREATED_AT"],
        "use_cases": ["Token economy analysis", "Reward distribution", "Player earnings tracking", "Game mode profitability"]
    },
    
    # ===== VOXIE & NFT DATA =====
    "VOXIE_DETAILS": {
        "description": "Detailed information about Voxie NFTs including stats, equipment, class, race, and rarity",
        "schema": "ANALYTICS",
        "key_columns": ["ID", "NAME", "CLASS", "RACE", "RARITY", "STRENGTH", "DEXTERITY", "INTELLIGENCE", "ARMOR", "WEAPONS"],
        "use_cases": ["NFT analysis", "Character balance", "Rarity distribution", "Equipment optimization"]
    },
    
    "VOXIE_TEAM_COMPOSITIONS": {
        "description": "Analysis of team compositions and their performance in battles",
        "schema": "ANALYTICS", 
        "key_columns": ["TEAM_ID", "VOXIE_IDS", "GAME_MODE", "WIN_RATE", "USAGE_COUNT"],
        "use_cases": ["Meta analysis", "Team composition effectiveness", "Strategic insights"]
    },
    
    # ===== MARKETPLACE & ECONOMY =====
    "MARKETPLACE_SALES": {
        "description": "All marketplace transactions including NFT sales, item trades, and token exchanges",
        "schema": "ANALYTICS",
        "key_columns": ["ID", "USER_ID", "ITEM_TYPE", "ITEM_ID", "TOTAL_PRICE", "UNIT_PRICE", "QUANTITY", "TRANSACTION_TYPE", "CREATED_AT"],
        "use_cases": ["Market analysis", "Price trends", "Trading volume", "Economic health"]
    },
    
    "TRANSACTION_DETAILS": {
        "description": "Detailed transaction records for all in-game and game website marketplace, forge, sales, services, etc. Token Claims and othereconomic activities",
        "schema": "ANALYTICS",
        "key_columns": ["TRANSACTION_ID", "USER_ID", "ORIGIN", "TRANSACTION_TYPE", "AMOUNT", "TOKEN_TYPE", "CREATED_AT"],
        "use_cases": ["Financial analysis", "Token flow tracking", "Revenue analysis"]
    },
    
    # ===== ITEMS & EQUIPMENT =====
    "ITEM_DETAILS": {
        "description": "Master item catalog with stats, rarity, and classification information",
        "schema": "ANALYTICS",
        "key_columns": ["ITEM_ID", "ITEM_NAME", "ITEM_TYPE", "RARITY", "CLASS", "STATS", "SOURCE"],
        "use_cases": ["Item analysis", "Rarity distribution", "Equipment balance"]
    },
    
    "DAILY_ITEM_USAGE": {
        "description": "Daily usage statistics for all items and equipment in battles",
        "schema": "ANALYTICS",
        "key_columns": ["DATE", "ITEM_ID", "USAGE_COUNT", "WIN_RATE", "GAME_MODE"],
        "use_cases": ["Item popularity", "Equipment effectiveness", "Meta trends"]
    },
    
    "INVENTORY_DETAILS": {
        "description": "Player inventory snapshots showing item ownership and quantities",
        "schema": "ANALYTICS",
        "key_columns": ["USER_ID", "ITEM_ID", "QUANTITY", "LAST_UPDATED"],
        "use_cases": ["Inventory analysis", "Item distribution", "Wealth analysis"]
    },
    
    # ===== RENTAL SYSTEM =====
    "RENTAL_DETAILS": {
        "description": "NFT rental transactions and terms between players",
        "schema": "ANALYTICS",
        "key_columns": ["RENTAL_ID", "OWNER_ID", "RENTER_ID", "NFT_ID", "RENTAL_PRICE", "DURATION", "START_DATE", "END_DATE"],
        "use_cases": ["Rental market analysis", "NFT utilization", "Secondary market trends"]
    },
    
    "RENTAL_NFT_DETAILS": {
        "description": "Details of NFTs available for rental including pricing and availability",
        "schema": "ANALYTICS",
        "key_columns": ["NFT_ID", "OWNER_ID", "RENTAL_PRICE", "AVAILABILITY", "RENTAL_COUNT"],
        "use_cases": ["Rental supply analysis", "Pricing strategies", "NFT utilization rates"]
    },
    
    "LIVE_USER_SCORE_RANKS": {
        "description": "Real-time player scores and current rankings",
        "schema": "ANALYTICS",
        "key_columns": ["USER_ID", "CURRENT_SCORE", "CURRENT_RANK", "LAST_UPDATED"],
        "use_cases": ["Live leaderboards", "Current standings", "Real-time analytics"]
    },
    
    # ===== FORGE & CRAFTING =====
    "FORGE_TRANSACTIONS": {
        "description": "Item crafting and forging transactions including recipes and outcomes",
        "schema": "ANALYTICS",
        "key_columns": ["TRANSACTION_ID", "USER_ID", "RECIPE_ID", "INPUT_ITEMS", "OUTPUT_ITEMS", "COST", "CREATED_AT"],
        "use_cases": ["Crafting analysis", "Recipe popularity", "Resource consumption"]
    },
    
    # ===== PACK SYSTEM =====
    "PACK_DETAILS": {
        "description": "Information about purchasable packs and their contents",
        "schema": "ANALYTICS",
        "key_columns": ["PACK_ID", "PACK_TYPE", "PRICE", "CONTENTS", "RARITY_DISTRIBUTION"],
        "use_cases": ["Pack analysis", "Monetization tracking", "Content distribution"]
    },
    
    "PACK_ITEM_DETAILS": {
        "description": "Detailed breakdown of items contained within packs",
        "schema": "ANALYTICS",
        "key_columns": ["PACK_ID", "ITEM_ID", "QUANTITY", "RARITY", "DROP_RATE"],
        "use_cases": ["Pack contents analysis", "Drop rate verification", "Value analysis"]
    },
    
    # ===== ADDITIONAL ANALYTICS TABLES =====
    "USER_HARDWARE": {
        "description": "Player hardware specifications and device information for performance optimization",
        "schema": "ANALYTICS",
        "key_columns": ["USERID", "USERNAME", "PLATFORM", "DEVICE_MODEL", "CPU", "MEMORY", "GRAPHICS_DEVICE_NAME"],
        "use_cases": ["Device performance analysis", "Platform distribution", "Hardware compatibility", "System requirements planning"]
    },
    
    "DAILY_PLAYER_BATTLE_DETAILS": {
        "description": "Detailed daily battle statistics per player including performance metrics",
        "schema": "ANALYTICS",
        "key_columns": ["PLAYER_ID", "DATE", "BATTLE_COUNT", "WIN_RATE", "AVERAGE_DURATION", "TOTAL_DAMAGE"],
        "use_cases": ["Player performance tracking", "Battle analytics", "Skill progression analysis"]
    },
    
    "DAILY_USERS_TOKEN_DISTRIBUTION": {
        "description": "Daily token distribution patterns across user base",
        "schema": "ANALYTICS",
        "key_columns": ["DATE", "USER_ID", "TOKEN_TYPE", "AMOUNT_DISTRIBUTED", "DISTRIBUTION_REASON"],
        "use_cases": ["Token economy analysis", "Distribution fairness", "Economic balance"]
    },
    
    "BATTLE_ITEM_REWARDS": {
        "description": "Item rewards earned through battle participation and victory",
        "schema": "ANALYTICS",
        "key_columns": ["BATTLE_ID", "USER_ID", "ITEM_ID", "QUANTITY", "REWARD_TYPE", "BATTLE_OUTCOME"],
        "use_cases": ["Battle reward analysis", "Item acquisition tracking", "Victory incentives"]
    },
    
    "TEAM_COMPOSITION_BY_VOXIE": {
        "description": "Analysis of team compositions and their effectiveness by individual Voxie",
        "schema": "ANALYTICS",
        "key_columns": ["VOXIE_ID", "TEAM_COMPOSITION", "WIN_RATE", "USAGE_COUNT", "GAME_MODE"],
        "use_cases": ["Voxie effectiveness", "Team synergy analysis", "Character balance"]
    },
    
    "NFT_ITEMS_DETAILS": {
        "description": "Comprehensive NFT item catalog with metadata and ownership tracking",
        "schema": "ANALYTICS",
        "key_columns": ["NFT_ID", "ITEM_TYPE", "RARITY", "OWNER_ID", "CREATION_DATE", "LAST_TRANSFER"],
        "use_cases": ["NFT analytics", "Ownership tracking", "Asset valuation", "Market analysis"]
    },
    
    "DAILY_GEAR_USAGE": {
        "description": "Daily equipment and gear usage statistics across all players",
        "schema": "ANALYTICS",
        "key_columns": ["DATE", "GEAR_ID", "USAGE_COUNT", "WIN_RATE", "PLAYER_COUNT"],
        "use_cases": ["Equipment popularity", "Gear effectiveness", "Meta analysis"]
    },
    
    "USERS_UPDATED_BALANCES": {
        "description": "User balance change tracking for all token types",
        "schema": "ANALYTICS",
        "key_columns": ["USER_ID", "TOKEN_TYPE", "BALANCE_BEFORE", "BALANCE_AFTER", "CHANGE_REASON", "UPDATED_AT"],
        "use_cases": ["Balance tracking", "Token flow analysis", "Financial auditing"]
    },
    
    "DAILY_PLAYER_COUNT_BY_GAMEMODE": {
        "description": "Daily active player counts segmented by game mode",
        "schema": "ANALYTICS",
        "key_columns": ["DATE", "GAME_MODE", "UNIQUE_PLAYERS", "TOTAL_SESSIONS", "AVERAGE_SESSION_LENGTH"],
        "use_cases": ["Game mode popularity", "Player engagement", "Mode-specific analytics"]
    },
    
    "VOXIE_TEAM_COMPOSITIONS_ENCOUNTER": {
        "description": "Team composition performance in specific encounter types",
        "schema": "ANALYTICS",
        "key_columns": ["ENCOUNTER_TYPE", "TEAM_COMPOSITION", "SUCCESS_RATE", "AVERAGE_DURATION"],
        "use_cases": ["Encounter difficulty", "Team optimization", "Content balancing"]
    },
    
    "PLAYERS_BATTLES_HISTORY": {
        "description": "Complete battle history for all players with detailed outcomes",
        "schema": "ANALYTICS",
        "key_columns": ["BATTLE_ID", "PLAYER_ID", "OPPONENT_ID", "OUTCOME", "DURATION", "BATTLE_DATE"],
        "use_cases": ["Battle history analysis", "Player matchmaking", "Performance tracking"]
    },
    
    "DAILY_PLAYERS_ENCOUNTERS": {
        "description": "Daily encounter participation and success rates per player",
        "schema": "ANALYTICS",
        "key_columns": ["DATE", "PLAYER_ID", "ENCOUNTER_TYPE", "ATTEMPTS", "SUCCESSES", "REWARDS_EARNED"],
        "use_cases": ["Encounter engagement", "Success rate analysis", "Content difficulty"]
    },
    
    "BATTLE_ITEM_USAGE": {
        "description": "Item usage during battles including consumables and equipment",
        "schema": "ANALYTICS",
        "key_columns": ["BATTLE_ID", "PLAYER_ID", "ITEM_ID", "USAGE_COUNT", "EFFECTIVENESS"],
        "use_cases": ["Item effectiveness in battle", "Combat balance", "Strategic analysis"]
    },
    
    "EQUIPMENT_WIN_RATE": {
        "description": "Win rate analysis for different equipment combinations and loadouts",
        "schema": "ANALYTICS",
        "key_columns": ["VOXIE_CLASS", "GAME_MODE", "HEAD", "BODY", "HANDS", "LEGS", "RIGHTHAND", "LEFTHAND", "ACCESSORY", "COMPANION", "WIN_RATE", "BATTLE_COUNT"],
        "use_cases": ["Equipment effectiveness", "Loadout optimization", "Meta analysis", "Balance insights"]
    },
    
    "VOXIE_TEAM_WIN_RATE": {
        "description": "Win rate analysis for different Voxie team compositions",
        "schema": "ANALYTICS",
        "key_columns": ["TEAM_COMPOSITION", "GAME_MODE", "WIN_RATE", "BATTLE_COUNT", "AVERAGE_DURATION"],
        "use_cases": ["Team effectiveness", "Composition optimization", "Strategic insights"]
    },
    
    "BATTLE_VOXIE_EQUIPMENT_DETAILS": {
        "description": "Detailed equipment information for Voxies used in specific battles",
        "schema": "ANALYTICS",
        "key_columns": ["BATTLE_ID", "VOXIE_ID", "EQUIPMENT_DETAILS", "STATS_BONUS", "PERFORMANCE"],
        "use_cases": ["Equipment impact analysis", "Battle performance correlation", "Gear optimization"]
    },

}

# Helper functions for table discovery
def get_table_info(table_name):
    """Get information about a specific table"""
    return TABLES.get(table_name.upper(), {})

def get_tables_by_schema(schema):
    """Get all tables in a specific schema"""
    return {k: v for k, v in TABLES.items() if v.get('schema') == schema.upper()}

def get_tables_by_use_case(use_case):
    """Find tables relevant to a specific use case"""
    relevant_tables = {}
    for table_name, table_info in TABLES.items():
        if any(use_case.lower() in uc.lower() for uc in table_info.get('use_cases', [])):
            relevant_tables[table_name] = table_info
    return relevant_tables

def get_all_table_names():
    """Get list of all table names"""
    return list(TABLES.keys()) 