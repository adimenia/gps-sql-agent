"""LLM Integration Service for OpenAI and Anthropic."""

import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from enum import Enum
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_sql(
        self, 
        question: str, 
        schema_context: str,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate SQL query from natural language question."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client for SQL generation and explanations."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        return self._client
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> str:
        """Generate a response using OpenAI GPT."""
        try:
            client = self._get_client()
            
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_sql(
        self, 
        question: str, 
        schema_context: str,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate SQL query from natural language question."""
        system_message = f"""You are a SQL expert for a sports analytics database. 
Generate ONLY the SQL query without any explanation or markdown formatting.

Database Schema:
{schema_context}

Rules:
1. Generate PostgreSQL-compatible SQL only
2. Use proper table and column names from the schema
3. Include appropriate WHERE clauses for data filtering
4. Use JOINs when data spans multiple tables
5. Return only the SQL query, no explanations
6. Use LIMIT clauses for queries that might return many rows"""

        prompt = f"Question: {question}\n\nSQL Query:"
        
        if examples:
            examples_text = "\n\nExamples:\n"
            for example in examples:
                examples_text += f"Q: {example['question']}\nSQL: {example['sql']}\n\n"
            prompt = examples_text + prompt
        
        return await self.generate_response(
            prompt=prompt,
            system_message=system_message,
            max_tokens=500,
            temperature=0.1
        )


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude client for SQL generation and explanations."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Get or create Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
        return self._client
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> str:
        """Generate a response using Anthropic Claude."""
        try:
            client = self._get_client()
            
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_message:
                kwargs["system"] = system_message
            
            response = await client.messages.create(**kwargs)
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_sql(
        self, 
        question: str, 
        schema_context: str,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate SQL query from natural language question."""
        system_message = f"""You are a SQL expert for a sports analytics database. 
Generate ONLY the SQL query without any explanation or markdown formatting.

Database Schema:
{schema_context}

Rules:
1. Generate PostgreSQL-compatible SQL only
2. Use proper table and column names from the schema
3. Include appropriate WHERE clauses for data filtering
4. Use JOINs when data spans multiple tables
5. Return only the SQL query, no explanations
6. Use LIMIT clauses for queries that might return many rows"""

        prompt = f"Question: {question}\n\nSQL Query:"
        
        if examples:
            examples_text = "\n\nExamples:\n"
            for example in examples:
                examples_text += f"Q: {example['question']}\nSQL: {example['sql']}\n\n"
            prompt = examples_text + prompt
        
        return await self.generate_response(
            prompt=prompt,
            system_message=system_message,
            max_tokens=500,
            temperature=0.1
        )


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration."""
    
    @staticmethod
    def create_client() -> BaseLLMClient:
        """Create appropriate LLM client based on available API keys."""
        
        # Check for OpenAI API key
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            logger.info("Using OpenAI client")
            return OpenAIClient(api_key=settings.openai_api_key)
        
        # Check for Anthropic API key
        if hasattr(settings, 'anthropic_api_key') and settings.anthropic_api_key:
            logger.info("Using Anthropic client")
            return AnthropicClient(api_key=settings.anthropic_api_key)
        
        # Fallback to mock client for development
        logger.warning("No LLM API keys configured, using mock client")
        return MockLLMClient()


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing and development."""
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> str:
        """Generate a mock response."""
        await asyncio.sleep(0.1)  # Simulate API delay
        return f"Mock response for: {prompt[:50]}..."
    
    async def generate_sql(
        self, 
        question: str, 
        schema_context: str,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate a mock SQL query."""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Return a simple mock query based on common patterns
        if "athlete" in question.lower():
            return "SELECT * FROM athletes LIMIT 10;"
        elif "activity" in question.lower():
            return "SELECT * FROM activities LIMIT 10;"
        elif "event" in question.lower():
            return "SELECT * FROM events LIMIT 10;"
        elif "effort" in question.lower():
            return "SELECT * FROM efforts LIMIT 10;"
        else:
            return "SELECT COUNT(*) FROM activities;"


# Convenience function to get configured LLM client
async def get_llm_client() -> BaseLLMClient:
    """Get the configured LLM client."""
    return LLMClientFactory.create_client()