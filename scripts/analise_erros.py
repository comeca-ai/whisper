#!/usr/bin/env python3

import pandas as pd
import re
from collections import Counter

def analyze_transcription_errors():
    # Carregar dados
    df = pd.read_csv('/workspaces/whisper/teste_estrategico_20260108_043428.csv')
    
    print("🔍 === ANÁLISE DE ERROS NAS TRANSCRIÇÕES ===")
    print()
    
    # Análise de repetições excessivas
    print("🔄 PROBLEMAS DE REPETIÇÃO")
    print("=" * 50)
    
    repetition_cases = []
    for _, row in df.iterrows():
        text = row['text']
        if text:
            # Procurar por padrões repetitivos
            repetitions = re.findall(r'\b(\w+)(?:\s*,\s*\1){3,}', text)  # palavras repetidas 4+ vezes
            if repetitions:
                repetition_cases.append({
                    'arquivo': row['audio_file'],
                    'modelo': f"{row['engine']}/{row['model']}",
                    'repetições': repetitions,
                    'texto_sample': text[:100] + "..."
                })
    
    if repetition_cases:
        for case in repetition_cases:
            print(f"📁 {case['arquivo']}")
            print(f"🤖 {case['modelo']}")
            print(f"🔄 Repetições encontradas: {case['repetições']}")
            print(f"📝 Texto: {case['texto_sample']}")
            print()
    else:
        print("✅ Nenhum caso grave de repetição encontrado")
        print()
    
    # Análise de erros de transcrição por categoria
    print("❌ TIPOS DE ERROS MAIS COMUNS")
    print("=" * 50)
    
    error_patterns = {
        'Palavras inventadas': [],
        'Nomes próprios errados': [],
        'Termos técnicos errados': [],
        'Repetições excessivas': [],
        'Pontuação incorreta': []
    }
    
    # Analisar cada transcrição
    for _, row in df.iterrows():
        text = row['text']
        if not text:
            continue
            
        # Palavras inventadas ou muito estranhas
        weird_words = re.findall(r'\b(Bereg|dreta|chau|dore|doação|maestônia|Becanismo|Bequanismo|fetalóx|fetalóxico|fita-lóxica)\b', text, re.IGNORECASE)
        if weird_words:
            error_patterns['Palavras inventadas'].append({
                'arquivo': row['audio_file'],
                'modelo': f"{row['engine']}/{row['model']}",
                'palavras': weird_words
            })
        
        # Nomes próprios
        wrong_names = re.findall(r'\b(Johnathan|Berek|Orto)\b', text)
        if wrong_names:
            error_patterns['Nomes próprios errados'].append({
                'arquivo': row['audio_file'], 
                'modelo': f"{row['engine']}/{row['model']}",
                'nomes': wrong_names
            })
            
        # Termos técnicos
        tech_errors = re.findall(r'\b(fita-lóxica|fetalóx|fetalóxico|Fitalox|baccélia|bacténea|vírus|vírus)\b', text)
        if tech_errors:
            error_patterns['Termos técnicos errados'].append({
                'arquivo': row['audio_file'],
                'modelo': f"{row['engine']}/{row['model']}",
                'termos': tech_errors
            })
            
        # Repetições de conectivos
        excessive_ands = len(re.findall(r'\be, e, e, e', text))
        if excessive_ands > 0:
            error_patterns['Repetições excessivas'].append({
                'arquivo': row['audio_file'],
                'modelo': f"{row['engine']}/{row['model']}",
                'tipo': f"'e, e, e...' ({excessive_ands} ocorrências)"
            })
    
    # Mostrar resultados por categoria
    for categoria, erros in error_patterns.items():
        if erros:
            print(f"🔸 {categoria}: {len(erros)} casos")
            for erro in erros[:3]:  # Mostrar apenas os primeiros 3
                arquivo_short = erro['arquivo'].split(' ')[-1]  # Pegar apenas a parte final do nome
                print(f"   📁 {arquivo_short} | 🤖 {erro['modelo']}")
                if 'palavras' in erro:
                    print(f"      Palavras: {erro['palavras']}")
                elif 'nomes' in erro:
                    print(f"      Nomes: {erro['nomes']}")
                elif 'termos' in erro:
                    print(f"      Termos: {erro['termos']}")
                elif 'tipo' in erro:
                    print(f"      Tipo: {erro['tipo']}")
            if len(erros) > 3:
                print(f"      ... e mais {len(erros) - 3} casos")
            print()
    
    # Comparar erros entre modelos
    print("⚖️ COMPARAÇÃO DE ERROS ENTRE MODELOS")
    print("=" * 50)
    
    tiny_errors = 0
    base_errors = 0
    
    for _, row in df.iterrows():
        text = row['text']
        if not text:
            continue
            
        # Contar palavras problemáticas
        problematic_patterns = [
            r'\b(Bereg|dreta|chau|dore|Becanismo|fetalóx)\b',
            r'\be, e, e, e',
            r'\bfita-lóxica, a fita-lóxica',
        ]
        
        error_count = 0
        for pattern in problematic_patterns:
            error_count += len(re.findall(pattern, text, re.IGNORECASE))
            
        if row['model'] == 'tiny':
            tiny_errors += error_count
        elif row['model'] == 'base':
            base_errors += error_count
    
    print(f"🤖 Whisper Tiny: {tiny_errors} erros detectados")
    print(f"🤖 Whisper Base: {base_errors} erros detectados")
    
    if tiny_errors < base_errors:
        print(f"✅ Whisper Tiny tem {base_errors - tiny_errors} erros a menos")
    elif base_errors < tiny_errors:
        print(f"✅ Whisper Base tem {tiny_errors - base_errors} erros a menos")
    else:
        print("🤝 Ambos os modelos têm performance similar em erros")
    print()
    
    # Casos mais problemáticos
    print("🚨 CASOS MAIS PROBLEMÁTICOS")
    print("=" * 40)
    
    problematic_files = []
    for _, row in df.iterrows():
        text = row['text']
        if not text:
            continue
            
        # Calcular "score de problema"
        problem_score = 0
        
        # Repetições excessivas (peso 3)
        problem_score += len(re.findall(r'\be, e, e', text)) * 3
        problem_score += len(re.findall(r'fita-lóxica, a fita-lóxica', text)) * 3
        
        # Palavras inventadas (peso 2)
        problem_score += len(re.findall(r'\b(Bereg|dreta|chau|Becanismo|fetalóxico)\b', text)) * 2
        
        # Nomes errados (peso 1)
        problem_score += len(re.findall(r'\b(Johnathan|Orto)\b', text))
        
        if problem_score > 0:
            problematic_files.append({
                'arquivo': row['audio_file'],
                'modelo': f"{row['engine']}/{row['model']}",
                'score': problem_score,
                'duracao': row['duration'],
                'texto_sample': text[:80] + "..."
            })
    
    # Ordenar por score de problema
    problematic_files.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"📊 Encontrados {len(problematic_files)} casos com problemas")
    print()
    
    for i, case in enumerate(problematic_files[:5], 1):  # Top 5 mais problemáticos
        arquivo_short = case['arquivo'].split(' at ')[0].replace('WhatsApp ', '')
        print(f"{i}. 📁 {arquivo_short}")
        print(f"   🤖 {case['modelo']} | 🔥 Score: {case['score']} | ⏱️ {case['duracao']}s")
        print(f"   📝 \"{case['texto_sample']}\"")
        print()
    
    # Recomendações
    print("💡 RECOMENDAÇÕES PARA MELHORIA")
    print("=" * 40)
    print("1. 🎯 Para nomes próprios: Usar glossário personalizado")
    print("2. 🔧 Para termos técnicos: Configurar vocabulário específico")
    print("3. 🛑 Para repetições: Ajustar temperatura ou usar pós-processamento")
    print("4. 📊 Whisper Tiny ainda é melhor opção apesar dos erros menores")
    print("5. 🧹 Implementar limpeza automática de repetições excessivas")

if __name__ == "__main__":
    analyze_transcription_errors()