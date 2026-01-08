#!/usr/bin/env python3

import os
import time
import json
import requests
from pathlib import Path
import pandas as pd
from datetime import datetime

def test_transcription_simple(audio_file, engine, model):
    """Teste simples sem retry complexo"""
    url = "http://localhost:8000/transcribe"
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            data = {'engine': engine, 'model': model}
            
            start_time = time.time()
            response = requests.post(url, files=files, data=data, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '').strip()
                return {
                    'success': True,
                    'text': text,
                    'language': result.get('language', 'N/A'),
                    'duration': round(end_time - start_time, 2),
                    'word_count': len(text.split()) if text else 0,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'text': '',
                    'language': 'N/A',
                    'duration': round(end_time - start_time, 2),
                    'word_count': 0,
                    'error': f"HTTP {response.status_code}"
                }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'language': 'N/A',
            'duration': 0,
            'word_count': 0,
            'error': str(e)[:50] + "..."
        }

def main():
    print("🎯 === TESTE ESTRATÉGICO: WHISPER TINY & BASE COM TODOS OS ÁUDIOS ===")
    print()
    
    # Verificar API
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API não está funcionando")
            return
        print("✅ API funcionando")
    except:
        print("❌ Não foi possível conectar à API")
        return
    
    # Listar áudios
    audio_dir = Path("/workspaces/whisper/audios")
    audio_files = sorted(list(audio_dir.glob("*.ogg")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav")))
    
    print(f"📁 {len(audio_files)} arquivos de áudio encontrados")
    
    # Apenas os 2 modelos que sabemos que funcionam
    models = [
        ('whisper', 'tiny'),
        ('whisper', 'base')
    ]
    
    print(f"🤖 Testando {len(models)} modelos")
    print()
    
    results = []
    total_tests = len(audio_files) * len(models)
    test_count = 0
    
    for audio_file in audio_files:
        print(f"🎵 {audio_file.name}")
        
        for engine, model in models:
            test_count += 1
            print(f"   [{test_count:2d}/{total_tests}] {engine}/{model} ... ", end="", flush=True)
            
            result = test_transcription_simple(audio_file, engine, model)
            
            result.update({
                'audio_file': audio_file.name,
                'engine': engine,
                'model': model,
                'timestamp': datetime.now().isoformat()
            })
            
            results.append(result)
            
            if result['success']:
                text_preview = result['text'][:40] + "..." if len(result['text']) > 40 else result['text']
                print(f"✅ {result['duration']:5.2f}s │ {result['language']} │ {result['word_count']:2d} palavras │ \"{text_preview}\"")
            else:
                print(f"❌ {result['error']}")
            
            time.sleep(1)  # Pausa entre testes
        
        print()
    
    # Análise final
    print("📊 === RESULTADOS FINAIS ===")
    print()
    
    df = pd.DataFrame(results)
    
    # Salvar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"/workspaces/whisper/teste_estrategico_{timestamp}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    # Estatísticas
    total_tests = len(df)
    successes = df['success'].sum()
    success_rate = (successes / total_tests * 100) if total_tests > 0 else 0
    
    print("📈 RESUMO GERAL")
    print("=" * 40)
    print(f"🧪 Testes executados: {total_tests}")
    print(f"✅ Sucessos: {successes}")
    print(f"❌ Falhas: {total_tests - successes}")
    print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    print()
    
    if successes > 0:
        successful = df[df['success'] == True]
        
        # Comparação entre modelos
        print("🏆 COMPARAÇÃO ENTRE MODELOS")
        print("=" * 50)
        model_comparison = successful.groupby(['engine', 'model']).agg({
            'duration': ['mean', 'min', 'max'],
            'word_count': 'mean',
            'success': 'count'
        }).round(2)
        model_comparison.columns = ['Tempo_Médio', 'Tempo_Mín', 'Tempo_Máx', 'Palavras_Média', 'Sucessos']
        print(model_comparison)
        print()
        
        # Performance por áudio
        print("🎵 PERFORMANCE POR ÁUDIO")
        print("=" * 60)
        audio_performance = df.groupby('audio_file').agg({
            'success': ['sum', 'count'],
            'duration': 'mean'
        }).round(2)
        audio_performance.columns = ['Sucessos', 'Total', 'Tempo_Médio']
        audio_performance['Taxa_Sucesso'] = (audio_performance['Sucessos'] / audio_performance['Total'] * 100).round(1)
        print(audio_performance.sort_values('Taxa_Sucesso', ascending=False))
        print()
        
        # Melhores transcrições
        print("📝 MELHORES TRANSCRIÇÕES")
        print("=" * 60)
        best_transcriptions = successful.nlargest(5, 'word_count')
        for _, row in best_transcriptions.iterrows():
            print(f"🎵 {row['audio_file']}")
            print(f"🤖 {row['engine']}/{row['model']} │ {row['duration']}s │ {row['word_count']} palavras")
            text_clean = row['text'][:80] + "..." if len(row['text']) > 80 else row['text']
            print(f"📝 \"{text_clean}\"")
            print()
        
        # Velocidade
        fastest = successful.loc[successful['duration'].idxmin()]
        slowest = successful.loc[successful['duration'].idxmax()]
        
        print("⚡ VELOCIDADE")
        print("=" * 30)
        print(f"🚀 Mais rápido: {fastest['engine']}/{fastest['model']} ({fastest['duration']}s)")
        print(f"🐌 Mais lento: {slowest['engine']}/{slowest['model']} ({slowest['duration']}s)")
        print()
        
        print("🎯 RECOMENDAÇÃO")
        print("=" * 30)
        avg_tiny = successful[successful['model'] == 'tiny']['duration'].mean()
        avg_base = successful[successful['model'] == 'base']['duration'].mean()
        
        if avg_tiny < avg_base:
            print("🏆 Whisper TINY é mais rápido em média")
            print(f"   Tiny: {avg_tiny:.2f}s vs Base: {avg_base:.2f}s")
        else:
            print("🏆 Whisper BASE é mais rápido em média") 
            print(f"   Base: {avg_base:.2f}s vs Tiny: {avg_tiny:.2f}s")
    
    # Mostrar falhas se houver
    failed = df[df['success'] == False]
    if not failed.empty:
        print("\\n❌ FALHAS")
        print("=" * 20)
        failure_summary = failed.groupby(['engine', 'model'])['error'].count()
        for (engine, model), count in failure_summary.items():
            print(f"   {engine}/{model}: {count} falhas")
    
    print()
    print("=" * 60)
    print(f"💾 Resultados salvos em: {csv_file}")
    print("🎉 Análise concluída!")

if __name__ == "__main__":
    main()