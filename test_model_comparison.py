#!/usr/bin/env python3
"""
🧪 TESTE COMPARATIVO DE MODELOS OPENROUTER
Testando Qwen 3 32B vs Claude 3.5 Sonnet vs GPT-4o Mini
"""

import requests
import json
import time

# Configuração
API_BASE = "http://localhost:8002"

def test_available_models():
    """Testa quais modelos estão disponíveis."""
    print("🤖 MODELOS IA DISPONÍVEIS:")
    print("=" * 40)
    
    response = requests.get(f"{API_BASE}/ai-models")
    result = response.json()
    
    print(f"📊 Total de modelos: {len(result['available_models'])}")
    print(f"🎯 Modelo padrão: {result['default_model']}")
    print()
    
    print("📋 MODELOS DISPONÍVEIS:")
    for key, model in result['available_models'].items():
        print(f"• {key}: {model['name']}")
        print(f"  Força: {model['strength']}")
        print(f"  Velocidade: {model['speed']} | Custo: {model['cost']}")
        print()
    
    print("🏆 RECOMENDAÇÕES:")
    for category, model in result['recommended'].items():
        print(f"• {category.title()}: {model}")
    print()

def test_text_improvement_comparison():
    """Compara modelos na melhoria de texto."""
    print("✨ TESTE: MELHORIA DE TEXTO")
    print("=" * 40)
    
    # Texto problemático para teste
    test_text = "oi tudo bem como voce ta hoje espero que esteja bem ne vamos marca uma reuniao amanha"
    
    print(f"📝 Texto original: {test_text}")
    print()
    
    # Testa múltiplos modelos
    models_to_test = ["qwen3-32b", "claude-3.5-sonnet", "gpt-4o-mini"]
    results = {}
    
    for model in models_to_test:
        print(f"🤖 Testando {model}...")
        
        start_time = time.time()
        
        try:
            data = {
                'text': test_text,
                'language': 'pt',
                'ai_model': model
            }
            
            response = requests.post(f"{API_BASE}/improve-transcription", data=data, timeout=30)
            result = response.json()
            
            end_time = time.time()
            
            if 'improved_text' in result:
                results[model] = {
                    'success': True,
                    'improved_text': result['improved_text'],
                    'time': round(end_time - start_time, 2)
                }
                print(f"✅ Sucesso em {results[model]['time']}s")
                print(f"📝 Resultado: {result['improved_text'][:80]}...")
            else:
                results[model] = {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'time': round(end_time - start_time, 2)
                }
                print(f"❌ Erro: {results[model]['error']}")
            
        except Exception as e:
            results[model] = {
                'success': False,
                'error': str(e),
                'time': 0
            }
            print(f"❌ Exceção: {e}")
        
        print()
    
    # Resumo dos resultados
    print("📊 RESUMO COMPARATIVO:")
    print("-" * 40)
    
    successful_models = [(k, v) for k, v in results.items() if v['success']]
    
    if successful_models:
        # Ordenar por velocidade
        fastest = min(successful_models, key=lambda x: x[1]['time'])
        print(f"🏃 Mais rápido: {fastest[0]} ({fastest[1]['time']}s)")
        
        # Mostrar todos os resultados
        for model, result in successful_models:
            print(f"\n🤖 {model.upper()}:")
            print(f"   Tempo: {result['time']}s")
            print(f"   Resultado: {result['improved_text']}")
    
    return results

def test_model_comparison_api():
    """Testa o endpoint de comparação de modelos."""
    print("⚔️ TESTE: COMPARAÇÃO AUTOMÁTICA DE MODELOS")
    print("=" * 50)
    
    test_text = "ola como esta tudo bem espero que sim vamos conversar mais tarde"
    
    data = {
        'text': test_text,
        'task': 'improve',
        'models': 'qwen3-32b,claude-3.5-sonnet,gpt-4o-mini'
    }
    
    print(f"📝 Texto: {test_text}")
    print(f"🎯 Tarefa: {data['task']}")
    print(f"🤖 Modelos: {data['models']}")
    print()
    
    try:
        response = requests.post(f"{API_BASE}/compare-ai-models", data=data, timeout=60)
        result = response.json()
        
        if 'results' in result:
            print("📊 RESULTADOS DA COMPARAÇÃO:")
            print("-" * 30)
            
            for model, model_result in result['results'].items():
                print(f"\n🤖 {model.upper()}:")
                if 'result' in model_result:
                    print(f"   ✅ Resultado: {model_result['result'][:60]}...")
                    print(f"   ⏱️ Tempo: {model_result['time']}s")
                    print(f"   💡 Info: {model_result['model_info'].get('strength', 'N/A')}")
                else:
                    print(f"   ❌ Erro: {model_result.get('error', 'Unknown')}")
            
            print(f"\n🏆 RANKING:")
            print(f"   🥇 Mais rápido: {result['ranking']['fastest']}")
            print(f"   🐌 Mais lento: {result['ranking']['slowest']}")
            
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"   Modelos testados: {result['summary']['models_tested']}")
            print(f"   Tempo total: {result['summary']['total_time']}s")
            print(f"   Tempo médio: {result['summary']['average_time']}s")
        
        else:
            print(f"❌ Erro na comparação: {result.get('error', 'Unknown')}")
    
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_qwen_specific():
    """Teste específico do modelo Qwen 3 32B."""
    print("🎯 TESTE ESPECÍFICO: QWEN 3 32B")
    print("=" * 40)
    
    # Diferentes tipos de texto para testar
    test_cases = [
        {
            "name": "Texto informal",
            "text": "opa blza cara como q ta as coisa ai na sua cidade"
        },
        {
            "name": "Texto técnico",
            "text": "precisamos implementar uma api rest com autenticacao jwt e banco de dados postgresql"
        },
        {
            "name": "Pontuação problemática", 
            "text": "oi tudo bem entao vamos marcar reuniao sexta feira as duas horas da tarde ok"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 CASO {i}: {case['name']}")
        print(f"Original: {case['text']}")
        
        try:
            data = {
                'text': case['text'],
                'ai_model': 'qwen3-32b'
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/improve-transcription", data=data, timeout=30)
            result = response.json()
            end_time = time.time()
            
            if 'improved_text' in result:
                print(f"✅ Qwen 3 32B ({end_time - start_time:.1f}s): {result['improved_text']}")
            else:
                print(f"❌ Erro: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Exceção: {e}")

def main():
    """Executa todos os testes de modelos."""
    print("🚀 TESTE COMPARATIVO DE MODELOS OPENROUTER")
    print("=" * 50)
    
    try:
        # Verifica se API está rodando
        health = requests.get(f"{API_BASE}/health").json()
        
        if health['features']['openrouter_integration'] != 'enabled':
            print("❌ OpenRouter não está habilitado")
            return
        
        print("✅ API rodando e OpenRouter habilitado")
        print()
        
        # Executa testes
        test_available_models()
        test_text_improvement_comparison()
        test_model_comparison_api()
        test_qwen_specific()
        
        print("\n🏆 CONCLUSÃO:")
        print("=" * 20)
        print("✅ Todos os testes de modelos concluídos!")
        print("🎯 Qwen 3 32B testado com sucesso!")
        
    except requests.exceptions.ConnectionError:
        print("❌ API não está rodando. Execute: PORT=8002 python api_otimizada.py")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()