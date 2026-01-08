#!/usr/bin/env python3

import requests
import time
import json
from pathlib import Path

def test_optimized_api():
    """
    Testar a API otimizada vs API original com os áudios mais problemáticos
    """
    print("🧪 === TESTE: API OTIMIZADA vs API ORIGINAL ===")
    print()
    
    # Áudios mais problemáticos identificados na análise
    problem_audios = [
        "WhatsApp Ptt 2026-01-06 at 20.49.19.ogg",  # Score: 108 - repetições massivas
        "WhatsApp Video 2026-01-06 at 10.21.33.mp3",  # Score: 44 - repetições técnicas
        "WhatsApp Audio 2026-01-07 at 13.59.15.ogg"   # Score: 2 - palavras inventadas
    ]
    
    audio_dir = Path("/workspaces/whisper/audios")
    
    print("🎯 Testando com os 3 áudios mais problemáticos:")
    for audio in problem_audios:
        print(f"   - {audio}")
    print()
    
    # Configurações de teste
    configurations = [
        {
            "name": "🔵 API Original (baseline)",
            "url": "http://localhost:8000/transcribe",
            "params": {
                "model": "tiny",
                "temperature": 0.0
            }
        },
        {
            "name": "🟢 API Otimizada (anti-repetição)",
            "url": "http://localhost:8001/transcribe", 
            "params": {
                "model": "tiny",
                "temperature": 0.0,
                "compression_ratio_threshold": 2.0,  # Mais rigoroso
                "condition_on_previous_text": False,  # Reduz dependência de contexto
                "clean_repetitions": True,
                "apply_corrections": True,
                "use_multiple_temperatures": True
            }
        },
        {
            "name": "🟡 API Otimizada (base model + otimizações)",
            "url": "http://localhost:8001/transcribe",
            "params": {
                "model": "base",  # Modelo mais confiável
                "temperature": 0.0,
                "compression_ratio_threshold": 1.8,  # Ainda mais rigoroso
                "condition_on_previous_text": False,
                "clean_repetitions": True,
                "apply_corrections": True,
                "initial_prompt": "Transcrição de áudio em português brasileiro, sem repetições desnecessárias."
            }
        }
    ]
    
    results = []
    
    # Testar cada configuração com cada áudio
    for audio_name in problem_audios:
        audio_path = audio_dir / audio_name
        if not audio_path.exists():
            print(f"❌ Áudio não encontrado: {audio_name}")
            continue
            
        print(f"🎵 Testando: {audio_name}")
        
        for config in configurations:
            print(f"   {config['name']} ... ", end="", flush=True)
            
            try:
                with open(audio_path, 'rb') as f:
                    files = {'file': f}
                    data = config['params']
                    
                    start_time = time.time()
                    response = requests.post(
                        config['url'], 
                        files=files, 
                        data=data, 
                        timeout=60
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        result = response.json()
                        text = result.get('text', '')
                        original_text = result.get('original_text', text)
                        
                        # Calcular métricas de qualidade
                        repetition_score = calculate_repetition_score(text)
                        invention_score = calculate_invention_score(text)
                        
                        results.append({
                            'audio': audio_name,
                            'config': config['name'],
                            'duration': round(end_time - start_time, 2),
                            'text': text,
                            'original_text': original_text,
                            'repetition_score': repetition_score,
                            'invention_score': invention_score,
                            'word_count': len(text.split()) if text else 0,
                            'success': True
                        })
                        
                        print(f"✅ {end_time - start_time:.2f}s | Rep: {repetition_score} | Inv: {invention_score}")
                        
                    else:
                        print(f"❌ HTTP {response.status_code}")
                        results.append({
                            'audio': audio_name,
                            'config': config['name'],
                            'success': False,
                            'error': f"HTTP {response.status_code}"
                        })
                        
            except requests.exceptions.ConnectionError:
                print("❌ Conexão falhou (API não está rodando?)")
                results.append({
                    'audio': audio_name,
                    'config': config['name'],
                    'success': False,
                    'error': 'Connection failed'
                })
            except Exception as e:
                print(f"❌ {str(e)[:30]}...")
                results.append({
                    'audio': audio_name,
                    'config': config['name'],
                    'success': False,
                    'error': str(e)[:50]
                })
            
            time.sleep(1)  # Pausa entre testes
        
        print()
    
    # Analisar resultados
    print("📊 === ANÁLISE COMPARATIVA ===")
    print()
    
    successful_results = [r for r in results if r.get('success', False)]
    
    if successful_results:
        # Agrupar por configuração
        by_config = {}
        for result in successful_results:
            config = result['config']
            if config not in by_config:
                by_config[config] = []
            by_config[config].append(result)
        
        print("🏆 RANKING POR QUALIDADE (menor score de repetição/invenção = melhor)")
        print("=" * 70)
        
        config_scores = []
        for config, results_list in by_config.items():
            avg_rep = sum(r['repetition_score'] for r in results_list) / len(results_list)
            avg_inv = sum(r['invention_score'] for r in results_list) / len(results_list)
            avg_time = sum(r['duration'] for r in results_list) / len(results_list)
            total_score = avg_rep + avg_inv
            
            config_scores.append({
                'config': config,
                'avg_repetition': avg_rep,
                'avg_invention': avg_inv,
                'total_score': total_score,
                'avg_time': avg_time,
                'tests': len(results_list)
            })
        
        config_scores.sort(key=lambda x: x['total_score'])
        
        for i, score in enumerate(config_scores, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "🏅"
            print(f"{medal} {score['config']}")
            print(f"   Score Total: {score['total_score']:.2f} (Rep: {score['avg_repetition']:.2f} + Inv: {score['avg_invention']:.2f})")
            print(f"   Tempo Médio: {score['avg_time']:.2f}s | Testes: {score['tests']}")
            print()
        
        # Mostrar exemplos de melhoria
        print("📝 EXEMPLOS DE MELHORIA")
        print("=" * 50)
        
        for audio in problem_audios:
            audio_results = [r for r in successful_results if r['audio'] == audio]
            if len(audio_results) >= 2:
                print(f"🎵 {audio.split(' at ')[0].replace('WhatsApp ', '')}")
                
                for result in audio_results:
                    text_preview = result['text'][:80] + "..." if len(result['text']) > 80 else result['text']
                    print(f"   {result['config']}")
                    print(f"   📝 \"{text_preview}\"")
                    print(f"   📊 Rep: {result['repetition_score']} | Inv: {result['invention_score']}")
                    print()
    
    else:
        print("❌ Nenhum teste foi bem-sucedido. Verifique se as APIs estão rodando.")
    
    print("💡 COMO INICIAR AS APIs:")
    print("   Terminal 1: python api.py (porta 8000)")
    print("   Terminal 2: python api_otimizada.py (porta 8001)")

def calculate_repetition_score(text):
    """Calcular score de repetições (quanto maior, pior)"""
    if not text:
        return 0
    
    import re
    score = 0
    
    # Repetições de conectivos
    score += len(re.findall(r'\be, e, e', text)) * 10
    
    # Repetições de palavras técnicas
    score += len(re.findall(r'(\b\w+)(?:,? a \1){3,}', text)) * 5
    
    # Sequências longas repetitivas
    words = text.split()
    if len(words) > 20:
        # Contar palavras que se repetem mais de 5 vezes consecutivas
        i = 0
        while i < len(words) - 4:
            word = words[i]
            count = 1
            j = i + 1
            while j < len(words) and words[j] == word:
                count += 1
                j += 1
            if count >= 5:
                score += count * 2
            i = j
    
    return score

def calculate_invention_score(text):
    """Calcular score de palavras inventadas (quanto maior, pior)"""
    if not text:
        return 0
        
    import re
    invented_words = [
        'bereg', 'berek', 'dreta', 'chau', 'becanismo', 'fetalóxico', 
        'fetalóx', 'orto', 'johnathan', 'bacténea', 'maestônia', 'dore'
    ]
    
    score = 0
    text_lower = text.lower()
    
    for word in invented_words:
        score += len(re.findall(r'\b' + word + r'\b', text_lower))
    
    return score

if __name__ == "__main__":
    test_optimized_api()