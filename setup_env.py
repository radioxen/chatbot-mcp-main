#!/usr/bin/env python3
"""
Setup script for Voxies Slack Bot & Streamlit App
Helps users configure their environment variables
"""
import os
import shutil
from pathlib import Path

def main():
    print("🎮 Voxies Environment Setup")
    print("=" * 50)
    
    # Check if .env already exists
    env_file = Path(".env")
    template_file = Path("env.template")
    
    if env_file.exists():
        print("✅ .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Copy template to .env
    if template_file.exists():
        shutil.copy(template_file, env_file)
        print(f"📄 Created .env file from template")
    else:
        print("❌ env.template not found!")
        return
    
    print("\n🔧 Environment Configuration Required:")
    print("\n1. SLACK BOT TOKENS:")
    print("   - Go to https://api.slack.com/apps")
    print("   - Create a new app or select existing one")
    print("   - Get SLACK_BOT_TOKEN from 'OAuth & Permissions'")
    print("   - Get SLACK_APP_TOKEN from 'Socket Mode'")
    
    print("\n2. SNOWFLAKE DATABASE:")
    print("   - Set your Snowflake account, user, password")
    print("   - Configure warehouse, role, database, schema")
    
    print("\n3. AI/LLM PROVIDER:")
    print("   - Add your OPENAI_API_KEY")
    print("   - Or configure alternative providers")
    
    print(f"\n📝 Edit the .env file to add your actual credentials:")
    print(f"   {env_file.absolute()}")
    
    print("\n🚀 After configuration, you can run:")
    print("   Streamlit app: cd client && streamlit run app.py")
    print("   Slack bot:     cd slack_bot && python bot.py")
    print("   Docker:        docker-compose up")
    
    print("\n⚠️  SECURITY NOTE:")
    print("   - Never commit .env files to git")
    print("   - Keep your tokens and credentials secure")
    print("   - The .env file is already in .gitignore")

if __name__ == "__main__":
    main() 