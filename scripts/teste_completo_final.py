#!/usr/bin/env python3

import os
import time
import json
import requests
from pathlib import Path
import pandas as pd
from datetime import datetime
import signal
import sys

def signal_handler(sig, frame):
    print('\\n\\n⚠️ Teste interrompido pelo usuário')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def test_transcription_single(audio_file, engine, model, timeout=45):
    """Testa transcrição com um modelo específico"""
    url = "http://localhost:8000/transcribe"
    
    try:
        # Verificação rápida da API
        health_check = requests.get("http://localhost:8000/health", timeout=3)
        if health_check.status_code != 200:
            return {'success': False, 'text': '', 'language': 'N/A', 'duration': 0, 'error': 'API not healthy'}
        
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            data = {'engine': engine, 'model': model}
            
            start_time = time.time()
            response = requests.post(url, files=files, data=data, timeout=timeout)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'text': result.get('text', ''),
                    'language': result.get('language', 'N/A'),
                    'duration': end_time - start_time,
                    'error': None,
                    'word_count': len(result.get('text', '').split())
                }
            else:
                return {
                    'success': False,
                    'text': '',
                    'language': 'N/A',
                    'duration': end_time - start_time,
                    'error': f"HTTP {response.status_code}",
                    'word_count': 0
                }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'language': 'N/A',
            'duration': 0,
            'error': str(e)[:100],
            'word_count': 0
        }

def wait_for_api_ready(max_wait=20):
    """Espera a API ficar pronta"""
    print("⏳ Verificando API...")
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ API pronta!")
                return True
        except:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Aguardando... ({i}/{max_wait}s)")
    return False

def get_audio_info(audio_file):
    """Obtém informações básicas do arquivo de áudio"""
    try:
        size_mb = audio_file.stat().st_size / (1024 * 1024)
        return {'size_mb': round(size_mb, 2)}
    except:
        return {'size_mb': 0}

def main():
    print("🎙️ === TESTE FINAL: TODOS OS ÁUDIOS COM MODELOS ESTRATÉGICOS ===")
    print()
    
    if not wait_for_api_ready():
        print("❌ API não está disponível. Inicie com: python api.py")
        return
    
    # Listar todos os áudios
    audio_dir = Path("/workspaces/whisper/audios")
    if not audio_dir.exists():
        print(f"❌ Diretório não encontrado: {audio_dir}")
        return
    
    audio_files = sorted(list(audio_dir.glob("*.ogg")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav")))
    if not audio_files:
        print("❌ Nenhum arquivo de áudio encontrado")
        return
    
    print(f"📁 Encontrados {len(audio_files)} arquivos de áudio:")
    for i, audio in enumerate(audio_files, 1):
        info = get_audio_info(audio)
        print(f"   {i:2d}. {audio.name} ({info['size_mb']:.1f} MB)")
    print()
    
    # Modelos estratégicos (começando com os mais leves)
    strategic_models = [
        ('whisper', 'tiny'),       # Mais rápido
        ('whisper', 'base'),       # Boa qualidade/velocidade
        ('faster-whisper', 'tiny'), # Otimizado rápido
        ('faster-whisper', 'base'), # Otimizado qualidade
    ]
    
    print("🤖 Modelos estratégicos:")
    for i, (engine, model) in enumerate(strategic_models, 1):
        print(f"   {i}. {engine} / {model}")
    
    total_tests = len(audio_files) * len(strategic_models)
    print(f"\\n📊 Total: {len(audio_files)} áudios × {len(strategic_models)} modelos = {total_tests} testes")
    print()
    
    # Executar testes
    results = []
    start_time = time.time()
    
    for audio_idx, audio_file in enumerate(audio_files, 1):
        print(f"🎵 [{audio_idx}/{len(audio_files)}] {audio_file.name}")
        
        audio_results = []
        for model_idx, (engine, model) in enumerate(strategic_models, 1):
            test_num = (audio_idx - 1) * len(strategic_models) + model_idx
            print(f"   🤖 [{test_num:2d}/{total_tests}] {engine:>15}/{model:>5} ... ", end="", flush=True)
            
            result = test_transcription_single(audio_file, engine, model)
            
            result.update({
                'audio_file': audio_file.name,
                'engine': engine,
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'audio_size_mb': get_audio_info(audio_file)['size_mb']
            })
            
            results.append(result)
            audio_results.append(result)
            
            if result['success']:
                words = result['word_count']
                lang = result['language']
                duration = result['duration']
                print(f"✅ {duration:5.2f}s │ {lang:>2} │ {words:3d} palavras")
            else:
                error_short = str(result['error'])[:25] + "..." if len(str(result['error'])) > 25 else str(result['error'])
                print(f"❌ {error_short}")
            
            # Pausa estratégica para não sobrecarregar
            time.sleep(0.5)
        
        # Resumo do áudio
        successes = sum(1 for r in audio_results if r['success'])
        print(f"   📊 Resultado: {successes}/{len(strategic_models)} sucessos")
        print()
    
    elapsed_time = time.time() - start_time
    print(f"⏱️ Tempo total: {elapsed_time/60:.1f} minutos")
    print()
    
    # Salvar e analisar resultados
    df = pd.DataFrame(results)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    detailed_csv = f"/workspaces/whisper/teste_completo_{timestamp}.csv"
    df.to_csv(detailed_csv, index=False, encoding='utf-8')
    
    print("💾 === RELATÓRIO FINAL ===")
    print()
    
    # Estatísticas gerais
    total_tests = len(df)
    total_successes = df['success'].sum()
    success_rate = (total_successes / total_tests * 100) if total_tests > 0 else 0
    
    print("📈 RESUMO GERAL")
    print("=" * 50)
    print(f"🧪 Total de testes: {total_tests}")
    print(f"✅ Sucessos: {total_successes}")
    print(f"❌ Falhas: {total_tests - total_successes}")
    print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    print()
    
    if total_successes > 0:
        successful_df = df[df['success'] == True]
        
        print("🏆 RANKING DE MODELOS (por velocidade)")
        print("=" * 60)
        model_ranking = successful_df.groupby(['engine', 'model']).agg({
            'duration': ['mean', 'count'],
            'word_count': 'mean'
        }).round(2)
        model_ranking.columns = ['Tempo_Médio', 'Testes_OK', 'Palavras_Média']
        model_ranking = model_ranking.sort_values('Tempo_Médio')
        print(model_ranking)
        print()
        
        print("🎵 PERFORMANCE POR ÁUDIO")
        print("=" * 80)
        audio_perf = df.groupby('audio_file').agg({
            'success': ['sum', 'count'],
            'duration': 'mean',
            'audio_size_mb': 'first'
        }).round(2)
        audio_perf.columns = ['Sucessos', 'Total', 'Tempo_Médio', 'Tamanho_MB']
        audio_perf['Taxa_Sucesso'] = (audio_perf['Sucessos'] / audio_perf['Total'] * 100).round(1)
        audio_perf = audio_perf.sort_values('Taxa_Sucesso', ascending=False)
        print(audio_perf)
        print()
        
        print("📝 AMOSTRAS DE TRANSCRIÇÕES")
        print("=" * 70)
        # Mostrar as 5 melhores transcrições
        best_samples = successful_df.nlargest(3, 'word_count')
        for idx, row in best_samples.iterrows():
            text_sample = row['text'][:100] + "..." if len(row['text']) > 100 else row['text']
            print(f"🎵 {row['audio_file']}")
            print(f"🤖 {row['engine']}/{row['model']} │ {row['duration']:.2f}s │ {row['language']} │ {row['word_count']} palavras")
            print(f"📝 \"{text_sample}\"")
            print()
        
        # Identificar melhor modelo
        best_model = successful_df.loc[successful_df['duration'].idxmin()]
        print("🚀 MODELO MAIS RÁPIDO")
        print("=" * 30)
        print(f"🏆 {best_model['engine']}/{best_model['model']}")
        print(f"⏱️ {best_model['duration']:.2f}s")
        print(f"🎵 Testado em: {best_model['audio_file']}")
    
    # Análise de problemas
    failed_df = df[df['success'] == False]
    if not failed_df.empty:
        print("\\n❌ ANÁLISE DE FALHAS")
        print("=" * 40)
        
        failure_by_model = failed_df.groupby(['engine', 'model'])['error'].count().sort_values(ascending=False)
        print("Falhas por modelo:")
        for (engine, model), count in failure_by_model.items():
            print(f"  {engine}/{model}: {count} falhas")
        
        print("\\nTipos de erro:")
        error_types = failed_df['error'].value_counts().head(3)
        for error, count in error_types.items():
            error_brief = str(error)[:50] + "..." if len(str(error)) > 50 else str(error)
            print(f"  {count}x: {error_brief}")
    
    print("\\n" + "=" * 70)
    print(f"💾 Resultados detalhados salvos em: {detailed_csv}")
    print(f"⏱️ Teste concluído em {elapsed_time/60:.1f} minutos")
    print("🎉 Análise completa!")

if __name__ == "__main__":
    main()