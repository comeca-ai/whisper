#!/usr/bin/env python3

import os
import time
import json
import requests
from pathlib import Path
import pandas as pd
from datetime import datetime

def test_transcription(audio_file, engine, model):
    """Testa transcrição com um modelo específico"""
    url = "http://localhost:8000/transcribe"
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            data = {'engine': engine, 'model': model}
            
            start_time = time.time()
            response = requests.post(url, files=files, data=data, timeout=120)
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
                return {
                    'success': False,
                    'text': '',
                    'language': 'N/A',
                    'duration': end_time - start_time,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'language': 'N/A',
            'duration': 0,
            'error': str(e)
        }

def get_available_models():
    """Obtém modelos disponíveis da API"""
    try:
        response = requests.get("http://localhost:8000/models")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Erro ao obter modelos: {e}")
        return None

def main():
    print("🧪 === TESTE ABRANGENTE DE TODOS OS MODELOS COM TODOS OS ÁUDIOS ===")
    print()
    
    # Diretório dos áudios
    audio_dir = Path("/workspaces/whisper/audios")
    if not audio_dir.exists():
        print(f"❌ Diretório não encontrado: {audio_dir}")
        return
    
    # Listar áudios
    audio_files = list(audio_dir.glob("*.ogg")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav"))
    if not audio_files:
        print("❌ Nenhum arquivo de áudio encontrado")
        return
    
    print(f"📁 Encontrados {len(audio_files)} arquivos de áudio:")
    for audio in audio_files:
        print(f"   - {audio.name}")
    print()
    
    # Obter modelos disponíveis
    models_info = get_available_models()
    if not models_info:
        print("❌ Não foi possível obter informações dos modelos")
        return
    
    print("🤖 Modelos disponíveis:")
    available_engines = []
    
    if models_info['engines_available'].get('whisper', False):
        for model in models_info['whisper_models']:
            available_engines.append(('whisper', model))
            print(f"   - Whisper: {model}")
    
    if models_info['engines_available'].get('faster-whisper', False):
        for model in ['tiny', 'base', 'small', 'medium']:  # Modelos mais comuns
            available_engines.append(('faster-whisper', model))
            print(f"   - Faster Whisper: {model}")
    
    print(f"\n📊 Total de combinações a testar: {len(audio_files)} áudios × {len(available_engines)} modelos = {len(audio_files) * len(available_engines)} testes")
    print()
    
    # Executar testes
    results = []
    total_tests = len(audio_files) * len(available_engines)
    current_test = 0
    
    for audio_file in audio_files:
        print(f"🎵 Processando: {audio_file.name}")
        
        for engine, model in available_engines:
            current_test += 1
            print(f"   [{current_test}/{total_tests}] {engine}/{model}... ", end="", flush=True)
            
            result = test_transcription(audio_file, engine, model)
            
            # Adicionar informações do teste
            result.update({
                'audio_file': audio_file.name,
                'engine': engine,
                'model': model,
                'timestamp': datetime.now().isoformat()
            })
            
            results.append(result)
            
            if result['success']:
                print(f"✅ {result['duration']:.2f}s")
            else:
                print(f"❌ {result['error']}")
        
        print()
    
    # Criar DataFrame para análise
    df = pd.DataFrame(results)
    
    # Salvar resultados detalhados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    detailed_csv = f"/workspaces/whisper/resultados_detalhados_{timestamp}.csv"
    df.to_csv(detailed_csv, index=False)
    print(f"💾 Resultados detalhados salvos em: {detailed_csv}")
    
    # Gerar tabelas de análise
    print("\n📊 === RESULTADOS E ANÁLISES ===")
    print()
    
    # Tabela 1: Taxa de Sucesso por Modelo
    print("📈 1. TAXA DE SUCESSO POR MODELO")
    print("=" * 60)
    success_by_model = df.groupby(['engine', 'model']).agg({
        'success': ['count', 'sum']
    }).round(2)
    success_by_model.columns = ['Total_Testes', 'Sucessos']
    success_by_model['Taxa_Sucesso'] = (success_by_model['Sucessos'] / success_by_model['Total_Testes'] * 100).round(1)
    success_by_model['Taxa_Sucesso'] = success_by_model['Taxa_Sucesso'].astype(str) + '%'
    print(success_by_model)
    print()
    
    # Tabela 2: Tempo Médio por Modelo (só sucessos)
    print("⏱️ 2. TEMPO MÉDIO DE PROCESSAMENTO (segundos)")
    print("=" * 60)
    successful_df = df[df['success'] == True]
    if not successful_df.empty:
        time_by_model = successful_df.groupby(['engine', 'model'])['duration'].agg(['mean', 'min', 'max']).round(2)
        time_by_model.columns = ['Tempo_Médio', 'Tempo_Mín', 'Tempo_Máx']
        print(time_by_model)
    else:
        print("Nenhum teste bem-sucedido para análise de tempo")
    print()
    
    # Tabela 3: Desempenho por Áudio
    print("🎵 3. DESEMPENHO POR ARQUIVO DE ÁUDIO")
    print("=" * 80)
    audio_stats = df.groupby('audio_file').agg({
        'success': ['count', 'sum'],
        'duration': 'mean'
    }).round(2)
    audio_stats.columns = ['Total_Modelos', 'Sucessos', 'Tempo_Médio']
    audio_stats['Taxa_Sucesso'] = (audio_stats['Sucessos'] / audio_stats['Total_Modelos'] * 100).round(1)
    audio_stats['Taxa_Sucesso'] = audio_stats['Taxa_Sucesso'].astype(str) + '%'
    print(audio_stats)
    print()
    
    # Tabela 4: Melhores e Piores Resultados
    print("🏆 4. RANKING DE MODELOS")
    print("=" * 50)
    if not successful_df.empty:
        ranking = successful_df.groupby(['engine', 'model']).agg({
            'duration': 'mean',
            'success': 'count'
        }).round(2)
        ranking.columns = ['Tempo_Médio', 'Testes_Sucessos']
        ranking = ranking.sort_values('Tempo_Médio')
        print("🚀 Mais Rápidos (tempo médio):")
        print(ranking.head())
        print()
    
    # Tabela 5: Análise de Erros
    failed_df = df[df['success'] == False]
    if not failed_df.empty:
        print("❌ 5. ANÁLISE DE ERROS")
        print("=" * 50)
        error_analysis = failed_df.groupby(['engine', 'model'])['error'].count()
        error_analysis.name = 'Quantidade_Erros'
        print(error_analysis)
        print()
    
    # Resumo final
    print("📋 === RESUMO EXECUTIVO ===")
    print("=" * 40)
    total_successful = df['success'].sum()
    total_tests = len(df)
    overall_success_rate = (total_successful / total_tests * 100)
    
    print(f"✅ Testes realizados: {total_tests}")
    print(f"✅ Sucessos: {total_successful}")
    print(f"❌ Falhas: {total_tests - total_successful}")
    print(f"📊 Taxa de sucesso geral: {overall_success_rate:.1f}%")
    
    if not successful_df.empty:
        fastest_model = successful_df.loc[successful_df['duration'].idxmin()]
        print(f"🚀 Modelo mais rápido: {fastest_model['engine']}/{fastest_model['model']} ({fastest_model['duration']:.2f}s)")
        
        avg_time = successful_df['duration'].mean()
        print(f"⏱️ Tempo médio geral: {avg_time:.2f}s")
    
    print()
    print("💾 Arquivos gerados:")
    print(f"   - {detailed_csv}")
    print()
    print("🎉 Análise completa finalizada!")

if __name__ == "__main__":
    main()