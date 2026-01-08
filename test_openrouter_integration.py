#!/usr/bin/env python3
"""
Exemplo de uso da API Whisper Enhanced com integração OpenRouter
"""

import requests
import json
import time

# Configuração
API_BASE = "http://localhost:8001"
AUDIO_FILE = "audios/WhatsApp Audio 2026-01-07 at 18.21.06.ogg"

def test_basic_transcription():
    """Teste básico de transcrição."""
    print("🎵 Testando transcrição básica...")
    
    with open(AUDIO_FILE, 'rb') as f:
        files = {'file': f}
        data = {
            'model': 'base',
            'clean_repetitions': 'true',
            'apply_corrections': 'true'
        }
        
        response = requests.post(f"{API_BASE}/transcribe", files=files, data=data)
        result = response.json()
        
        print(f"✅ Transcrição: {result['text'][:100]}...")
        return result['text']

def test_transcribe_and_summarize():
    """Teste de transcrição + resumo com IA."""
    print("\n📝 Testando transcrição + resumo...")
    
    with open(AUDIO_FILE, 'rb') as f:
        files = {'file': f}
        data = {
            'model': 'base',
            'summary_length': 'short'
        }
        
        response = requests.post(f"{API_BASE}/transcribe-and-summarize", files=files, data=data)
        result = response.json()
        
        if 'summary' in result:
            print(f"✅ Resumo: {result['summary']}")
        else:
            print(f"❌ Erro no resumo: {result.get('summary_error', 'Unknown error')}")
        
        return result

def test_transcribe_and_translate():
    """Teste de transcrição + tradução."""
    print("\n🌐 Testando transcrição + tradução...")
    
    with open(AUDIO_FILE, 'rb') as f:
        files = {'file': f}
        data = {
            'model': 'base',
            'target_language': 'en'
        }
        
        response = requests.post(f"{API_BASE}/transcribe-and-translate", files=files, data=data)
        result = response.json()
        
        if 'translation' in result:
            print(f"✅ Tradução: {result['translation']['text'][:100]}...")
        else:
            print(f"❌ Erro na tradução: {result.get('translation_error', 'Unknown error')}")
        
        return result

def test_comprehensive_analysis():
    """Teste de análise completa."""
    print("\n🧠 Testando análise completa...")
    
    with open(AUDIO_FILE, 'rb') as f:
        files = {'file': f}
        data = {
            'model': 'base',
            'analysis_type': 'all'
        }
        
        response = requests.post(f"{API_BASE}/transcribe-and-analyze", files=files, data=data)
        result = response.json()
        
        if 'analysis' in result:
            analysis = result['analysis']
            
            if 'summary' in analysis:
                print(f"📋 Resumo: {analysis['summary'][:80]}...")
            
            if 'sentiment' in analysis:
                sentiment = analysis['sentiment']
                print(f"😊 Sentimento: {sentiment.get('sentiment', 'N/A')} (confiança: {sentiment.get('confidence', 0):.1f})")
            
            if 'action_items' in analysis and analysis['action_items']:
                print(f"✅ Ações encontradas: {len(analysis['action_items'])}")
                for i, action in enumerate(analysis['action_items'][:2], 1):
                    print(f"   {i}. {action[:50]}...")
            
            if 'improved_text' in analysis:
                print(f"📝 Texto melhorado disponível: {len(analysis['improved_text'])} chars")
        
        if 'errors' in result:
            print(f"⚠️ Erros: {result['errors']}")
        
        return result

def test_text_improvement():
    """Teste de melhoria de texto existente."""
    print("\n✨ Testando melhoria de texto...")
    
    # Primeiro pega uma transcrição
    original_text = test_basic_transcription()
    
    # Depois melhora
    data = {
        'text': original_text,
        'language': 'pt'
    }
    
    response = requests.post(f"{API_BASE}/improve-transcription", data=data)
    result = response.json()
    
    if 'improved_text' in result:
        print(f"✅ Texto original: {result['original_text'][:80]}...")
        print(f"✨ Texto melhorado: {result['improved_text'][:80]}...")
    else:
        print(f"❌ Erro na melhoria: {result.get('error', 'Unknown error')}")
    
    return result

def check_api_health():
    """Verifica status da API."""
    print("🏥 Verificando saúde da API...")
    
    response = requests.get(f"{API_BASE}/health")
    health = response.json()
    
    print(f"Status: {health['status']}")
    print(f"Versão: {health['version']}")
    print(f"Features: {health['features']}")
    
    return health

def main():
    """Executa todos os testes."""
    print("🚀 Testando Whisper Enhanced API com OpenRouter")
    print("=" * 50)
    
    try:
        # Verifica se API está rodando
        health = check_api_health()
        
        if health['features']['openrouter_integration'] == 'disabled':
            print("⚠️ OpenRouter não configurado - apenas testes básicos")
            test_basic_transcription()
            return
        
        # Testes com IA
        print("\n🤖 OpenRouter habilitado - executando testes completos")
        
        # Teste básico
        test_basic_transcription()
        
        # Testes com IA
        test_transcribe_and_summarize()
        test_transcribe_and_translate() 
        test_comprehensive_analysis()
        test_text_improvement()
        
        print("\n✅ Todos os testes concluídos!")
        
    except requests.exceptions.ConnectionError:
        print("❌ API não está rodando. Execute: python api_otimizada.py")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()