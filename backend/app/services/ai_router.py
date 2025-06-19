"""
Multi-AI Router Service
Routes requests to different AI models (OpenAI, Claude, Gemini)
"""

import openai
import anthropic
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import time
import asyncio
import json
from enum import Enum

from app.core.config import settings
from app.models.conversation import AIModel, ConversationMessage, MessageRole

class AIRouter:
    """Route AI requests to different models"""
    
    def __init__(self):
        # Initialize AI clients
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI model clients"""
        
        # OpenAI
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai
        
        # Anthropic Claude
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        
        # Google Gemini
        if settings.GOOGLE_AI_API_KEY:
            genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
            self.gemini_client = genai.GenerativeModel('gemini-pro')
    
    async def chat_completion(
        self,
        model: AIModel,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate chat completion using specified AI model
        
        Args:
            model: AI model to use
            messages: List of messages in OpenAI format
            temperature: Response randomness (0-1)
            max_tokens: Maximum response length
            system_prompt: Optional system prompt
        
        Returns:
            Dict with response, tokens used, and metadata
        """
        
        start_time = time.time()
        
        try:
            if model in [AIModel.OPENAI_GPT4, AIModel.OPENAI_GPT35]:
                return await self._openai_completion(model, messages, temperature, max_tokens, system_prompt)
            
            elif model in [AIModel.CLAUDE_3_OPUS, AIModel.CLAUDE_3_SONNET]:
                return await self._anthropic_completion(model, messages, temperature, max_tokens, system_prompt)
            
            elif model == AIModel.GEMINI_PRO:
                return await self._gemini_completion(messages, temperature, max_tokens, system_prompt)
            
            else:
                raise ValueError(f"Unsupported AI model: {model}")
                
        except Exception as e:
            end_time = time.time()
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "model": model,
                "tokens_used": 0,
                "response_time_ms": int((end_time - start_time) * 1000),
                "error": str(e)
            }
    
    async def _openai_completion(
        self,
        model: AIModel,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """OpenAI completion"""
        
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        # Prepare messages
        openai_messages = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        
        openai_messages.extend(messages)
        
        # Select model
        model_name = "gpt-4" if model == AIModel.OPENAI_GPT4 else "gpt-3.5-turbo"
        
        start_time = time.time()
        
        response = await self.openai_client.ChatCompletion.acreate(
            model=model_name,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        end_time = time.time()
        
        return {
            "response": response.choices[0].message.content,
            "model": model,
            "tokens_used": response.usage.total_tokens,
            "response_time_ms": int((end_time - start_time) * 1000),
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def _anthropic_completion(
        self,
        model: AIModel,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Claude completion"""
        
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        # Convert messages to Claude format
        claude_messages = []
        for msg in messages:
            claude_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Select model
        model_name = "claude-3-opus-20240229" if model == AIModel.CLAUDE_3_OPUS else "claude-3-sonnet-20240229"
        
        start_time = time.time()
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.anthropic_client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=claude_messages
            )
        )
        
        end_time = time.time()
        
        return {
            "response": response.content[0].text,
            "model": model,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "response_time_ms": int((end_time - start_time) * 1000),
            "finish_reason": "stop"
        }
    
    async def _gemini_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Gemini completion"""
        
        if not self.gemini_client:
            raise ValueError("Gemini client not initialized")
        
        # Convert messages to Gemini format
        conversation_text = ""
        if system_prompt:
            conversation_text += f"System: {system_prompt}\n\n"
        
        for msg in messages:
            role = "Human" if msg["role"] == "user" else "Assistant"
            conversation_text += f"{role}: {msg['content']}\n\n"
        
        conversation_text += "Assistant: "
        
        start_time = time.time()
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.gemini_client.generate_content(
                conversation_text,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
        )
        
        end_time = time.time()
        
        return {
            "response": response.text,
            "model": AIModel.GEMINI_PRO,
            "tokens_used": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
            "response_time_ms": int((end_time - start_time) * 1000),
            "finish_reason": "stop"
        }
    
    def get_available_models(self) -> List[AIModel]:
        """Get list of available AI models"""
        available = []
        
        if self.openai_client:
            available.extend([AIModel.OPENAI_GPT4, AIModel.OPENAI_GPT35])
        
        if self.anthropic_client:
            available.extend([AIModel.CLAUDE_3_OPUS, AIModel.CLAUDE_3_SONNET])
        
        if self.gemini_client:
            available.append(AIModel.GEMINI_PRO)
        
        return available
    
    def get_model_info(self, model: AIModel) -> Dict[str, Any]:
        """Get information about a specific model"""
        model_info = {
            AIModel.OPENAI_GPT4: {
                "name": "GPT-4",
                "provider": "OpenAI",
                "description": "Most capable model, excellent for complex reasoning",
                "strengths": ["Complex reasoning", "Code generation", "Creative writing"],
                "cost_per_1k_tokens": 0.03
            },
            AIModel.OPENAI_GPT35: {
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI", 
                "description": "Fast and efficient, good for most tasks",
                "strengths": ["Speed", "Efficiency", "General knowledge"],
                "cost_per_1k_tokens": 0.002
            },
            AIModel.CLAUDE_3_OPUS: {
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "description": "Highly capable model with strong reasoning",
                "strengths": ["Reasoning", "Analysis", "Ethical responses"],
                "cost_per_1k_tokens": 0.015
            },
            AIModel.CLAUDE_3_SONNET: {
                "name": "Claude 3 Sonnet",
                "provider": "Anthropic",
                "description": "Balanced model for most educational tasks",
                "strengths": ["Balance", "Helpfulness", "Safety"],
                "cost_per_1k_tokens": 0.003
            },
            AIModel.GEMINI_PRO: {
                "name": "Gemini Pro",
                "provider": "Google",
                "description": "Versatile model with multimodal capabilities",
                "strengths": ["Multimodal", "Reasoning", "Speed"],
                "cost_per_1k_tokens": 0.001
            }
        }
        
        return model_info.get(model, {"name": "Unknown", "provider": "Unknown"})

# Global AI router instance
ai_router = AIRouter()