"""
Exemplos de uso da API Whisper
"""
import requests
import json

# URL da API
API_URL = "https://laughing-eureka-pj9j5j55x6vwh6797-8000.app.github.dev"

# ========================================
# Exemplo 1: Transcrição simples
# ========================================
def transcricao_simples(arquivo_audio):
    """Transcrição com configurações padrão"""
    
    with open(arquivo_audio, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_URL}/transcribe-simple", files=files)
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Transcrição concluída!")
        print(f"Texto: {resultado['text']}")
        print(f"Idioma: {resultado['language']}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)


# ========================================
# Exemplo 2: Transcrição com opções
# ========================================
def transcricao_completa(arquivo_audio, idioma='pt', modelo='base'):
    """Transcrição com opções personalizadas"""
    
    with open(arquivo_audio, 'rb') as f:
        files = {'file': f}
        data = {
            'model': modelo,      # tiny, base, small, medium, large
            'language': idioma,   # pt, en, es, fr, etc
            'task': 'transcribe', # ou 'translate' para traduzir
            'temperature': 0.0,
            'verbose': False
        }
        response = requests.post(f"{API_URL}/transcribe", files=files, data=data)
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Transcrição concluída!")
        print(f"Texto: {resultado['text']}")
        print(f"\nSegmentos ({len(resultado['segments'])}):")
        for seg in resultado['segments']:
            print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
        return resultado
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        return None


# ========================================
# Exemplo 3: Traduzir para inglês
# ========================================
def traduzir_audio(arquivo_audio):
    """Traduz áudio para inglês"""
    
    with open(arquivo_audio, 'rb') as f:
        files = {'file': f}
        data = {
            'model': 'base',
            'task': 'translate'  # Traduz para inglês
        }
        response = requests.post(f"{API_URL}/transcribe", files=files, data=data)
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Tradução concluída!")
        print(f"Texto traduzido: {resultado['text']}")
        return resultado
    else:
        print(f"❌ Erro: {response.status_code}")


# ========================================
# Exemplo 4: Processar múltiplos arquivos
# ========================================
def processar_lote(lista_arquivos):
    """Processa múltiplos arquivos"""
    
    resultados = []
    for arquivo in lista_arquivos:
        print(f"\n📁 Processando: {arquivo}")
        with open(arquivo, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/transcribe-simple", files=files)
        
        if response.status_code == 200:
            resultado = response.json()
            resultados.append({
                'arquivo': arquivo,
                'texto': resultado['text'],
                'idioma': resultado['language']
            })
            print(f"✅ {arquivo}: {resultado['text'][:50]}...")
        else:
            print(f"❌ Erro ao processar {arquivo}")
    
    return resultados


# ========================================
# Exemplo 5: Salvar resultado em JSON
# ========================================
def transcrever_e_salvar(arquivo_audio, arquivo_saida='resultado.json'):
    """Transcreve e salva resultado em JSON"""
    
    with open(arquivo_audio, 'rb') as f:
        files = {'file': f}
        data = {'model': 'base', 'language': 'pt'}
        response = requests.post(f"{API_URL}/transcribe", files=files, data=data)
    
    if response.status_code == 200:
        resultado = response.json()
        
        # Salvar em JSON
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Resultado salvo em: {arquivo_saida}")
        return resultado
    else:
        print(f"❌ Erro: {response.status_code}")
        return None


# ========================================
# Exemplo 6: Stream de bytes (sem arquivo)
# ========================================
def transcrever_bytes(audio_bytes, nome_arquivo='audio.mp3'):
    """Transcreve diretamente de bytes (útil para gravações em tempo real)"""
    
    files = {'file': (nome_arquivo, audio_bytes, 'audio/mpeg')}
    response = requests.post(f"{API_URL}/transcribe-simple", files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erro: {response.status_code}")
        return None


# ========================================
# Uso dos exemplos
# ========================================
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python exemplo_uso_api.py <arquivo_audio>")
        print("\nExemplos:")
        print("  python exemplo_uso_api.py audio.mp3")
        print("  python exemplo_uso_api.py audio.wav")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    
    print("=" * 50)
    print("EXEMPLO 1: Transcrição Simples")
    print("=" * 50)
    transcricao_simples(arquivo)
    
    print("\n" + "=" * 50)
    print("EXEMPLO 2: Transcrição Completa")
    print("=" * 50)
    transcricao_completa(arquivo, idioma='pt', modelo='base')
    
    print("\n" + "=" * 50)
    print("EXEMPLO 3: Salvar em JSON")
    print("=" * 50)
    transcrever_e_salvar(arquivo, 'transcricao.json')
