"""
Shared LLM Factory for creating language models across different interfaces.

This module provides a clean, interface-agnostic way to create LLM instances
for use in Streamlit, Slack, or any other interface.
"""
import os
from typing import Optional, Dict, Any, List, Iterator, AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage, AIMessageChunk
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
from langchain_aws import ChatBedrock
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
import openai
import httpx
from pydantic import Field

from .config import MODEL_OPTIONS


class CustomChatOpenAI(BaseChatModel):
    """Custom OpenAI chat model that bypasses the LangChain ChatOpenAI initialization issues."""
    
    # Declare fields for Pydantic model
    client: Any = Field(default=None, exclude=True)
    async_client: Any = Field(default=None, exclude=True)
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=4096)
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs):
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)
        # Create custom httpx client that avoids proxies issue
        http_client = httpx.Client(
            timeout=30.0,
            # Don't pass proxies parameter at all
        )
        async_http_client = httpx.AsyncClient(
            timeout=30.0,
            # Don't pass proxies parameter at all
        )
        # Create OpenAI clients with custom httpx clients
        object.__setattr__(self, 'client', openai.OpenAI(
            api_key=api_key,
            http_client=http_client,
            timeout=30.0,
            max_retries=2,
        ))
        object.__setattr__(self, 'async_client', openai.AsyncOpenAI(
            api_key=api_key,
            http_client=async_http_client,
            timeout=30.0,
            max_retries=2,
        ))
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat response using OpenAI API directly."""
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
            else:
                openai_messages.append({"role": "user", "content": str(msg.content)})
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop,
            **kwargs
        )
        
        # Convert response to LangChain format
        message = AIMessage(content=response.choices[0].message.content)
        generation = ChatGeneration(message=message)
        
        return ChatResult(generations=[generation])
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream chat response using OpenAI API directly."""
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
            else:
                openai_messages.append({"role": "user", "content": str(msg.content)})
        
        # Call OpenAI API with streaming
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop,
            stream=True,
            **kwargs
        )
        
        # Stream the response
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                message = AIMessageChunk(content=chunk.choices[0].delta.content)
                print(f"DEBUG: _stream yielding type={type(message)} content={message.content[:20] if hasattr(message, 'content') else 'N/A'}")
                print(f"DEBUG: _stream ChatGenerationChunk type={ChatGenerationChunk}")
                yield ChatGenerationChunk(message=message)
    
    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Async stream chat response using OpenAI API directly."""
        print(f"DEBUG: _astream called with {len(messages)} messages")
        
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
            else:
                openai_messages.append({"role": "user", "content": str(msg.content)})
        
        print(f"DEBUG: OpenAI messages: {openai_messages}")
        
        # Check if we have function definitions in kwargs
        functions = kwargs.get('functions', None)
        function_call = kwargs.get('function_call', None)
        
        api_kwargs = {
            'model': self.model,
            'messages': openai_messages,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'stream': True
        }
        
        if stop:
            api_kwargs['stop'] = stop
        
        # Add function calling support
        if functions:
            api_kwargs['functions'] = functions
        if function_call:
            api_kwargs['function_call'] = function_call
        
        # Call OpenAI API with streaming
        response = await self.async_client.chat.completions.create(**api_kwargs)
        
        print(f"DEBUG: OpenAI response received")
        chunk_count = 0
        
        # Track function call data
        function_call_data = {"name": "", "arguments": ""}
        
        # Stream the response
        async for chunk in response:
            chunk_count += 1
            print(f"DEBUG: Processing chunk {chunk_count}: {chunk}")
            
            if chunk.choices and len(chunk.choices) > 0:
                choice = chunk.choices[0]
                if hasattr(choice, 'delta') and choice.delta:
                    # Handle regular content
                    content = choice.delta.content or ""
                    if content:
                        message = AIMessageChunk(content=content)
                        print(f"DEBUG: _astream yielding chunk with content: '{content[:20]}...'")
                        yield ChatGenerationChunk(message=message)
                    
                    # Handle function calls
                    elif hasattr(choice.delta, 'function_call') and choice.delta.function_call:
                        func_call = choice.delta.function_call
                        if func_call.name:
                            function_call_data["name"] = func_call.name
                        if func_call.arguments:
                            function_call_data["arguments"] += func_call.arguments
                    
                    # Handle completion
                    elif choice.finish_reason == 'function_call':
                        # Create function call message
                        import json
                        
                        # Parse function call arguments
                        try:
                            args = json.loads(function_call_data["arguments"])
                        except json.JSONDecodeError:
                            args = {}
                        
                        print(f"DEBUG: _astream yielding function call: {function_call_data['name']}")
                        yield ChatGenerationChunk(message=AIMessageChunk(
                            content="",
                            additional_kwargs={
                                "function_call": {
                                    "name": function_call_data["name"],
                                    "arguments": function_call_data["arguments"]
                                }
                            }
                        ))
                    
                    elif choice.finish_reason == 'stop':
                        # Yield an empty chunk to signal completion
                        message = AIMessageChunk(content="")
                        print(f"DEBUG: _astream yielding final empty chunk")
                        yield ChatGenerationChunk(message=message)
        
        print(f"DEBUG: _astream completed, processed {chunk_count} chunks")
        
        # Ensure we always yield at least one chunk
        if chunk_count == 0:
            print("DEBUG: No chunks received, yielding fallback response")
            message = AIMessageChunk(content="I apologize, but I didn't receive a proper response. Please try again.")
            yield ChatGenerationChunk(message=message)
    
    @property
    def _llm_type(self) -> str:
        return "custom-openai"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


class LLMFactory:
    """Factory for creating LLM instances based on provider and configuration."""
    
    @staticmethod
    def create_llm(llm_provider: str, config: Dict[str, Any] = None, **kwargs) -> Any:
        """
        Create a language model based on the selected provider.
        
        Args:
            llm_provider: The LLM provider name (OpenAI, Anthropic, etc.)
            config: Configuration dictionary containing API keys and settings
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Configured LLM instance
        """
        if config is None:
            config = {}
            
        if llm_provider == "OpenAI":
            # Use provided key or environment variable
            openai_key = (
                config.get("api_key") or 
                os.getenv("OPENAI_API_KEY")
            )
            if not openai_key:
                raise ValueError("OpenAI API key not provided")
            
            # Use custom OpenAI wrapper to bypass proxies issue
            return CustomChatOpenAI(
                api_key=openai_key,
                model=MODEL_OPTIONS['OpenAI'],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 4096),
            )
            
        elif llm_provider == "Antropic":
            anthropic_key = (
                config.get("api_key") or 
                os.getenv("ANTHROPIC_API_KEY")
            )
            if not anthropic_key:
                raise ValueError("Anthropic API key not provided")
                
            return ChatAnthropic(
                anthropic_api_key=anthropic_key,
                model=MODEL_OPTIONS['Antropic'],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 4096),
            )
            
        elif llm_provider == "Bedrock":
            import boto3
            # Initialize Bedrock client
            bedrock = boto3.client(
                'bedrock-runtime',
                region_name=config.get("region_name"),
                aws_access_key_id=config.get("aws_access_key"),
                aws_secret_access_key=config.get("aws_secret_key"),
            )
            return ChatBedrock(
                client=bedrock,
                model_id=MODEL_OPTIONS['Bedrock'],
                **kwargs
            )
            
        elif llm_provider == "Google":
            google_key = (
                config.get("api_key") or 
                os.getenv("GOOGLE_API_KEY")
            )
            if not google_key:
                raise ValueError("Google API key not provided")
                
            return ChatGoogleGenerativeAI(
                google_api_key=google_key,
                model=MODEL_OPTIONS['Google'],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 4096),
                max_retries=2,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    @staticmethod
    def get_response(prompt: str, llm_provider: str, config: Dict[str, Any] = None) -> str:
        """Get a simple response from the LLM."""
        try:
            llm = LLMFactory.create_llm(llm_provider, config)
            message = HumanMessage(content=prompt)
            response = llm.invoke([message])
            return response.content
        except Exception as e:
            raise Exception(f"Error during LLM invocation: {str(e)}")

    @staticmethod
    def get_response_stream(
        prompt: str,
        llm_provider: str,
        config: Dict[str, Any] = None,
        system: Optional[str] = None,
        temperature: float = 0.9,
        max_tokens: int = 4096,
        **kwargs
    ):
        """Get a streaming response from the LLM."""
        try:
            # Update kwargs with generation params
            kwargs.update({
                "temperature": temperature,
                "max_tokens": max_tokens,
                "streaming": True
            })

            # Create the LLM with streaming enabled
            llm = LLMFactory.create_llm(llm_provider, config, **kwargs)

            # Compose messages
            messages = []
            if system:
                messages.append(SystemMessage(content=system))
            messages.append(HumanMessage(content=prompt))

            # Stream the response
            return llm.stream(messages)
            
        except Exception as e:
            raise Exception(f"Error during streaming: {str(e)}") 