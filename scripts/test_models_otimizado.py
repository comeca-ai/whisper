#!/usr/bin/env python3

import os
import time
import json
import requests
from pathlib import Path
import pandas as pd
from datetime import datetime

def test_transcription_robust(audio_file, engine, model, max_retries=3):
    """Testa transcrição com retry e timeout"""
    url = "http://localhost:8000/transcribe"
    
    for attempt in range(max_retries):
        try:
            # Verificar se API está online
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            if health_response.status_code != 200:
                print(f"   API não está saudável (tentativa {attempt+1})")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                else:
                    return {'success': False, 'text': '', 'language': 'N/A', 'duration': 0, 'error': 'API unhealthy'}
            
            with open(audio_file, 'rb') as f:
                files = {'file': f}
                data = {'engine': engine, 'model': model}
                
                start_time = time.time()
                response = requests.post(url, files=files, data=data, timeout=60)
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'text': result.get('text', ''),
                        'language': result.get('language', 'N/A'),
                        'duration': end_time - start_time,
                        'error': None
                    }
                else:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return {
                        'success': False,
                        'text': '',
                        'language': 'N/A',
                        'duration': end_time - start_time,
                        'error': f"HTTP {response.status_code}: {response.text}"
                    }
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"   Erro (tentativa {attempt+1}): {str(e)[:50]}... Tentando novamente...")
                time.sleep(3)
                continue
            return {
                'success': False,
                'text': '',
                'language': 'N/A',
                'duration': 0,
                'error': str(e)
            }

def wait_for_api(timeout=30):
    """Espera a API ficar disponível"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    return False

def main():
    print("🧪 === TESTE OTIMIZADO DE MODELOS COM ÁUDIOS ===")
    print()
    
    # Aguardar API
    print("⏳ Aguardando API ficar disponível...")
    if not wait_for_api():
        print("❌ API não está disponível")
        return
    print("✅ API está funcionando")
    print()
    
    # Diretório dos áudios
    audio_dir = Path("/workspaces/whisper/audios")
    if not audio_dir.exists():
        print(f"❌ Diretório não encontrado: {audio_dir}")
        return
    
    # Selecionar apenas 3 áudios para teste mais rápido
    all_audios = list(audio_dir.glob("*.ogg")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav"))
    audio_files = all_audios[:3] if len(all_audios) > 3 else all_audios
    
    print(f"📁 Testando com {len(audio_files)} arquivos de áudio:")
    for audio in audio_files:
        print(f"   - {audio.name}")
    print()
    
    # Modelos selecionados para teste estratégico
    test_models = [
        ('whisper', 'tiny'),
        ('whisper', 'base'),
        ('whisper', 'small'),
        ('faster-whisper', 'tiny'),
        ('faster-whisper', 'base')
    ]
    
    print("🤖 Modelos a testar:")
    for engine, model in test_models:
        print(f"   - {engine}: {model}")
    
    print(f"\\n📊 Total de testes: {len(audio_files)} × {len(test_models)} = {len(audio_files) * len(test_models)}")
    print()
    
    # Executar testes
    results = []
    total_tests = len(audio_files) * len(test_models)
    current_test = 0
    
    for audio_file in audio_files:
        print(f"🎵 Processando: {audio_file.name}")
        
        for engine, model in test_models:
            current_test += 1
            print(f"   [{current_test}/{total_tests}] {engine}/{model}... ", end="", flush=True)
            
            result = test_transcription_robust(audio_file, engine, model)
            
            # Adicionar informações do teste
            result.update({
                'audio_file': audio_file.name,
                'engine': engine,
                'model': model,
                'timestamp': datetime.now().isoformat()
            })
            
            results.append(result)
            
            if result['success']:
                text_preview = result['text'][:50] + "..." if len(result['text']) > 50 else result['text']
                print(f"✅ {result['duration']:.2f}s | {result['language']} | \"{text_preview}\"")
            else:
                error_preview = result['error'][:30] + "..." if len(str(result['error'])) > 30 else str(result['error'])
                print(f"❌ {error_preview}")
            
            # Pequena pausa entre testes para não sobrecarregar
            time.sleep(1)
        
        print()
    
    # Criar DataFrame para análise
    df = pd.DataFrame(results)
    
    # Salvar resultados detalhados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    detailed_csv = f"/workspaces/whisper/resultados_otimizados_{timestamp}.csv"
    df.to_csv(detailed_csv, index=False)
    print(f"💾 Resultados detalhados salvos em: {detailed_csv}")
    
    # Gerar tabelas de análise
    print("\\n📊 === RESULTADOS E ANÁLISES ===")
    print()
    
    # Estatísticas gerais
    total_successful = df['success'].sum()
    total_tests = len(df)
    overall_success_rate = (total_successful / total_tests * 100) if total_tests > 0 else 0
    
    print("📋 RESUMO GERAL")
    print("=" * 40)
    print(f"✅ Testes realizados: {total_tests}")
    print(f"✅ Sucessos: {total_successful}")
    print(f"❌ Falhas: {total_tests - total_successful}")
    print(f"📊 Taxa de sucesso geral: {overall_success_rate:.1f}%")
    print()
    
    if total_successful > 0:
        successful_df = df[df['success'] == True]
        
        # Tabela 1: Desempenho por Modelo
        print("🏆 RANKING DE DESEMPENHO POR MODELO")
        print("=" * 60)
        model_stats = successful_df.groupby(['engine', 'model']).agg({
            'duration': ['mean', 'min', 'max', 'count'],
            'success': 'count'
        }).round(2)
        
        model_stats.columns = ['Tempo_Médio', 'Tempo_Mín', 'Tempo_Máx', 'Count', 'Sucessos']
        model_stats = model_stats.drop('Count', axis=1)
        model_stats = model_stats.sort_values('Tempo_Médio')
        print(model_stats)
        print()
        
        # Tabela 2: Melhores resultados por áudio
        print("🎵 DESEMPENHO POR ARQUIVO DE ÁUDIO")
        print("=" * 70)
        audio_stats = df.groupby('audio_file').agg({
            'success': ['sum', 'count'],
            'duration': 'mean'
        }).round(2)
        audio_stats.columns = ['Sucessos', 'Total_Testes', 'Tempo_Médio']
        audio_stats['Taxa_Sucesso'] = ((audio_stats['Sucessos'] / audio_stats['Total_Testes']) * 100).round(1)
        print(audio_stats)
        print()
        
        # Mostrar algumas transcrições de exemplo
        print("📝 EXEMPLOS DE TRANSCRIÇÕES")
        print("=" * 60)
        sample_results = successful_df.head(3)
        for _, row in sample_results.iterrows():
            print(f"🎵 {row['audio_file']}")
            print(f"🤖 Modelo: {row['engine']}/{row['model']}")
            print(f"🌍 Idioma: {row['language']}")
            print(f"⏱️ Tempo: {row['duration']:.2f}s")
            print(f"📝 Texto: {row['text']}")
            print("-" * 60)
    
    # Análise de erros se houver
    failed_df = df[df['success'] == False]
    if not failed_df.empty:
        print("❌ ANÁLISE DE ERROS")
        print("=" * 40)
        error_counts = failed_df.groupby(['engine', 'model'])['error'].count().sort_values(ascending=False)
        print("Erros por modelo:")
        print(error_counts)
        print()
        
        # Tipos de erro mais comuns
        print("Tipos de erro mais comuns:")
        unique_errors = failed_df['error'].value_counts().head(5)
        for error, count in unique_errors.items():
            error_short = str(error)[:80] + "..." if len(str(error)) > 80 else str(error)
            print(f"  {count}x: {error_short}")
    
    print()
    print("🎉 Análise completa!")

if __name__ == "__main__":
    main()