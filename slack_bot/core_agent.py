"""
Core Voxies Agent - Uses shared agents package for consistency
"""
import asyncio
import os
import sys
import time
import traceback
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Add workspace to path (mounted in Docker)
if '/workspace' not in sys.path:
    sys.path.insert(0, '/workspace')

# Import shared modules from workspace
from agents import AppAgent

load_dotenv()

class SlackAppAgent:
    """
    Slack-specific wrapper for the shared AppAgent.
    Provides Slack-friendly response formatting while using the exact same agent logic.
    """
    
    def __init__(self):
        print("Initializing SlackAppAgent")
        
        # Use shared AppAgent with Slack-specific server config
        server_config = {
            "snowflake": {
                "command": "python",
                "args": ["/workspace/agents/snowflake_launcher.py"],
                "transport": "stdio"
            }
        }
        self.agent = AppAgent(server_config)
        print("SlackAppAgent created successfully")
        
    async def initialize(self):
        """Initialize the shared Voxies agent with debug parameters"""
        print("🔄 Initializing App Agent...")
        
        try:
            # Initialize with debug parameters
            debug_params = {
                'model_id': 'OpenAI',
                'temperature': 0.3,
                'max_tokens': 4096,
                'max_iterations': 20,
                'recursion_limit': 30,
                'dev_mode': True,
                'show_tool_calls': True,
                'show_supervisor': True
            }
            
            await self.agent.initialize(debug_params)
            tools = self.agent.get_tools()
            print(f"✅ Connected to MCP server with {len(tools)} tools")
            print("🎯 App Agent initialized successfully!")
            
            # Log available tools for debugging
            print("🔧 Available tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description[:100]}...")
                
        except Exception as e:
            print(f"❌ Failed to initialize app agent: {str(e)}")
            import traceback
            print(f"🔍 Debug traceback: {traceback.format_exc()}")
            raise
        
    async def process_query(self, user_message: str) -> str:
        """Process user query and format response for Slack with enhanced debugging"""
        start_time = time.time()
        print(f"Processing query: {user_message[:100]}...")
        
        if not self.agent.is_initialized():
            await self.initialize()
            
        try:
            print(f"🔍 DEBUG: Processing Slack query: {user_message}")
            
            # Use shared agent to process query
            response = await self.agent.process_query(user_message)
            
            print(f"🔍 DEBUG: Raw agent response: {response}")
            
            # Format response for Slack based on new message format
            if "messages" in response:
                output_parts = []
                tool_count = 0
                final_answer = ""
                
                for msg in response["messages"]:
                    if isinstance(msg, dict):
                        print(f"🔍 DEBUG: Processing message: {msg}")
                        
                        if msg.get("role") == "assistant":
                            if "tool" in msg and msg["tool"]:
                                # This is a tool execution
                                tool_count += 1
                                tool_summary = f"🔧 **Step {tool_count}**: {msg.get('name', 'Tool')}"
                                output_parts.append(tool_summary)
                                print(f"🔍 DEBUG: Found tool execution: {tool_summary}")
                            elif "name" in msg:
                                # Tool message with name
                                tool_count += 1
                                tool_summary = f"🔧 **Step {tool_count}**: {msg['name']}"
                                output_parts.append(tool_summary)
                                print(f"🔍 DEBUG: Found named tool: {tool_summary}")
                            else:
                                # Final answer
                                final_answer = msg.get("content", "")
                                print(f"🔍 DEBUG: Found final answer: {final_answer[:100]}...")
                
                # Format the complete response
                if final_answer:
                    if tool_count > 0:
                        # Show analysis steps + final answer
                        steps_summary = f"📊 **Analysis Steps ({tool_count} queries)**:\n" + "\n".join(output_parts)
                        formatted_response = f"🎮 **Voxies Analytics Results**\n\n{steps_summary}\n\n📋 **Answer**: {final_answer}"
                    else:
                        # Just the final answer
                        formatted_response = f"🎮 **Voxies Analytics**\n\n{final_answer}"
                    
                    print(f"🔍 DEBUG: Formatted response: {formatted_response[:200]}...")
                    
                    # Log successful query
                    duration_ms = (time.time() - start_time) * 1000
                    print(f"Query successful in {duration_ms:.2f}ms")
                    
                    return formatted_response
                else:
                    print("🔍 DEBUG: No final answer found")
                    return "I couldn't find a specific answer to your question. Please try rephrasing or asking about available data."
            else:
                print("🔍 DEBUG: No messages in response")
                return "I couldn't process your request. Please try again."
            
        except Exception as e:
            # Handle errors gracefully with enhanced debugging
            error_msg = str(e)
            duration_ms = (time.time() - start_time) * 1000
            
            print(f"❌ DEBUG: Error in process_query: {error_msg}")
            stack_trace = traceback.format_exc()
            print(f"🔍 DEBUG: Error traceback: {stack_trace}")
            
            print(f"Query failed in {duration_ms:.2f}ms")
            
            if "recursion" in error_msg.lower() or "maximum" in error_msg.lower():
                return f"⚠️ I reached the maximum number of analysis steps while processing your request. The analysis may be incomplete. Please try rephrasing your question or breaking it into smaller parts."
            else:
                return f"❌ Error processing your request: {error_msg}"
    
    async def cleanup(self):
        """Clean up agent resources"""
        await self.agent.cleanup()
        print("🔌 Disconnected from MCP server") 
