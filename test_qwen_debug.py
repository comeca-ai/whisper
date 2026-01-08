#!/usr/bin/env python3
"""
Teste simples do modelo Qwen 32B para verificar o problema
"""

import asyncio
import requests
import json
from openrouter_integration import OpenRouterClient

async def test_qwen_models():
    """Testar os modelos Qwen individualmente."""
    client = OpenRouterClient()
    
    test_text = "Oi André, tudo bom? Eu estava reunida com o Lauchova."
    
    models_to_test = [
        "qwen-7b",
        "qwen3-32b",
        "claude-3.5-sonnet",
        "gpt-4o-mini"
    ]
    
    for model in models_to_test:
        print(f"\n{'='*50}")
        print(f"Testando modelo: {model}")
        print(f"{'='*50}")
        
        try:
            # Teste simples de melhoria de transcrição
            result = await client.improve_transcription(test_text, model)
            print(f"✅ {model}: {result[:100]}...")
            
        except Exception as e:
            print(f"❌ {model}: ERRO - {str(e)}")
            
            # Tentar com uma mensagem mais simples
            try:
                messages = [{"role": "user", "content": "Diga olá"}]
                result = await client.chat_completion(messages, model=model, max_tokens=50)
                print(f"  Teste alternativo funcionou: {result['choices'][0]['message']['content']}")
            except Exception as e2:
                print(f"  Teste alternativo também falhou: {str(e2)}")

def list_available_models():
    """Listar modelos disponíveis na OpenRouter."""
    try:
        client = OpenRouterClient()
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {client.api_key}"}
        )
        
        if response.status_code == 200:
            models = response.json()
            print("Modelos Qwen disponíveis na OpenRouter:")
            for model in models.get('data', []):
                if 'qwen' in model['id'].lower():
                    print(f"  - {model['id']}: {model.get('name', 'N/A')}")
        else:
            print(f"Erro ao listar modelos: {response.status_code}")
            
    except Exception as e:
        print(f"Erro ao conectar com OpenRouter: {e}")

if __name__ == "__main__":
    print("Verificando modelos disponíveis...")
    list_available_models()
    
    print("\nTestando modelos...")
    asyncio.run(test_qwen_models())