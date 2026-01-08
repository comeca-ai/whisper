# OpenRouter Integration for Whisper Enhanced API
import os
import requests
import json
import time
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY', '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')
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://whisper-enhanced.railway.app",
            "X-Title": "Whisper Enhanced API"
        }
        
        # Modelos disponíveis com características
        self.available_models = {
            "claude-3.5-sonnet": {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "strength": "Excelente para texto, análise, tradução",
                "speed": "médio",
                "cost": "médio-alto"
            },
            "qwen3-32b": {
                "id": "qwen/qwen3-32b",
                "name": "Qwen 3 32B", 
                "strength": "Excelente qualidade, multilíngue, contexto grande",
                "speed": "médio",
                "cost": "baixo-médio"
            },
            "qwen-7b": {
                "id": "qwen/qwen-2.5-7b-instruct",
                "name": "Qwen 2.5 7B Instruct", 
                "strength": "Rápido, boa qualidade, multilíngue",
                "speed": "rápido",
                "cost": "baixo"
            },
            "qwen-72b": {
                "id": "qwen/qwen-2.5-72b-instruct",
                "name": "Qwen 2.5 72B Instruct", 
                "strength": "Excelente qualidade, contexto grande, multilíngue",
                "speed": "médio-lento",
                "cost": "médio"
            },
            "llama-3.1-70b": {
                "id": "meta-llama/llama-3.1-70b-instruct",
                "name": "Llama 3.1 70B",
                "strength": "Excelente custo-benefício, open source",
                "speed": "médio", 
                "cost": "médio"
            },
            "gpt-4o-mini": {
                "id": "openai/gpt-4o-mini",
                "name": "GPT-4o Mini",
                "strength": "Rápido e barato, boa qualidade",
                "speed": "muito rápido",
                "cost": "muito baixo"
            },
            "hermes-3": {
                "id": "nousresearch/hermes-3-llama-3.1-405b",
                "name": "Hermes 3 Llama 405B",
                "strength": "Modelo muito avançado, raciocínio complexo",
                "speed": "lento",
                "cost": "alto"
            }
        }
    
    async def chat_completion(
        self,
        messages: list,
        model: str = "claude-3.5-sonnet",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[Any, Any]:
        """Send chat completion request to OpenRouter."""
        
        # Resolve model ID
        model_id = self.available_models.get(model, {}).get('id', model)
        if model in self.available_models:
            logger.info(f"Using {self.available_models[model]['name']} - {self.available_models[model]['strength']}")
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {e}")
            raise Exception(f"OpenRouter API error: {str(e)}")
    
    async def summarize_text(self, text: str, model: str = "qwen3-32b", language: str = "pt") -> str:
        """Summarize transcribed text."""
        
        prompt = f"""Resuma o seguinte texto transcrito de áudio em português brasileiro.
        Mantenha os pontos principais e seja conciso:

        Texto: {text}
        
        Resumo:"""
        
        messages = [
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        response = await self.chat_completion(messages, model=model, temperature=0.3)
        return response['choices'][0]['message']['content'].strip()
    
    async def translate_text(self, text: str, target_language: str = "en", model: str = "qwen3-32b") -> str:
        """Translate transcribed text."""
        
        lang_names = {
            "en": "inglês",
            "es": "espanhol", 
            "fr": "francês",
            "de": "alemão",
            "it": "italiano"
        }
        
        target_name = lang_names.get(target_language, target_language)
        
        prompt = f"""Traduza o seguinte texto do português brasileiro para {target_name}.
        Mantenha o tom e contexto original:

        Texto: {text}
        
        Tradução para {target_name}:"""
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = await self.chat_completion(messages, model=model, temperature=0.2)
        return response['choices'][0]['message']['content'].strip()
    
    async def improve_transcription(self, text: str, model: str = "qwen3-32b") -> str:
        """Improve transcription quality using AI."""
        
        prompt = f"""Melhore esta transcrição de áudio em português brasileiro.
        Corrija erros de pontuação, capitalização e palavras que podem ter sido mal transcritas.
        Mantenha o sentido original:

        Transcrição original: {text}
        
        Transcrição melhorada:"""
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = await self.chat_completion(messages, model=model, temperature=0.1)
        return response['choices'][0]['message']['content'].strip()
    
    async def extract_action_items(self, text: str) -> list:
        """Extract action items from meeting transcription."""
        
        prompt = f"""Analise esta transcrição de reunião/conversa e extraia os principais pontos de ação.
        Retorne em formato de lista, apenas os pontos concretos mencionados:

        Transcrição: {text}
        
        Pontos de ação extraídos:"""
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = await self.chat_completion(messages, temperature=0.3)
        content = response['choices'][0]['message']['content'].strip()
        
        # Convert to list
        action_items = []
        for line in content.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                action_items.append(line.lstrip('-•* '))
        
        return action_items
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of transcribed text."""
        
        prompt = f"""Analise o sentimento do seguinte texto transcrito.
        Retorne apenas um JSON com: sentiment (positive/negative/neutral), confidence (0-1), e brief_explanation em português:

        Texto: {text}"""
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = await self.chat_completion(messages, temperature=0.1)
        content = response['choices'][0]['message']['content'].strip()
        
        try:
            # Try to parse JSON
            if content.startswith('```json'):
                content = content.replace('```json\n', '').replace('\n```', '')
            elif content.startswith('```'):
                content = content.replace('```\n', '').replace('\n```', '')
            
            return json.loads(content)
        except:
            # Fallback
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "brief_explanation": "Não foi possível analisar o sentimento automaticamente"
            }
    
    def list_available_models(self) -> Dict[str, Any]:
        """Lista modelos disponíveis com suas características."""
        return self.available_models
    
    async def compare_models(
        self, 
        text: str, 
        task: str = "improve", 
        models: list = ["qwen3-32b", "claude-3.5-sonnet", "gpt-4o-mini"]
    ) -> Dict[str, Any]:
        """Compara diferentes modelos na mesma tarefa."""
        
        results = {}
        
        for model in models:
            try:
                start_time = time.time()
                
                if task == "improve":
                    result = await self.improve_transcription(text, model)
                elif task == "summarize":
                    result = await self.summarize_text(text, model)
                elif task == "translate":
                    result = await self.translate_text(text, "en", model)
                else:
                    result = "Tarefa não suportada"
                
                end_time = time.time()
                
                results[model] = {
                    "result": result,
                    "time": round(end_time - start_time, 2),
                    "model_info": self.available_models.get(model, {})
                }
                
            except Exception as e:
                results[model] = {
                    "error": str(e),
                    "time": 0,
                    "model_info": self.available_models.get(model, {})
                }
        
        return results

# Global client instance
openrouter_client = OpenRouterClient()