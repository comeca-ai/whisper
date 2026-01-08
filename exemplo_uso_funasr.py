"""
Exemplos de uso da API com FunASR e Whisper
"""
import requests

API_URL = "http://localhost:8000"

# 1. Verificar modelos disponíveis
print("=== Modelos Disponíveis ===")
response = requests.get(f"{API_URL}/models")
print(response.json())
print()

# 2. Transcrição simples com Whisper (padrão)
print("=== Transcrição com Whisper (base) ===")
with open("audio.mp3", "rb") as f:
    response = requests.post(
        f"{API_URL}/transcribe",
        files={"file": f},
        data={
            "engine": "whisper",
            "model": "base",
            "language": "pt"
        }
    )
    print(response.json())
print()

# 3. Transcrição com FunASR (Paraformer)
print("=== Transcrição com FunASR (Paraformer) ===")
with open("audio.mp3", "rb") as f:
    response = requests.post(
        f"{API_URL}/transcribe",
        files={"file": f},
        data={
            "engine": "funasr",
            "model": "paraformer-zh",  # Para chinês
            # "model": "paraformer-en",  # Para inglês
            # "model": "paraformer-large-v2",  # Modelo grande multilíngue
        }
    )
    print(response.json())
print()

# 4. Comparar Whisper vs FunASR
print("=== Comparação Whisper vs FunASR ===")
audio_file = "audio.mp3"

# Whisper
with open(audio_file, "rb") as f:
    whisper_response = requests.post(
        f"{API_URL}/transcribe",
        files={"file": f},
        data={"engine": "whisper", "model": "small"}
    )
    whisper_result = whisper_response.json()

# FunASR
with open(audio_file, "rb") as f:
    funasr_response = requests.post(
        f"{API_URL}/transcribe",
        files={"file": f},
        data={"engine": "funasr", "model": "paraformer-large-v2"}
    )
    funasr_result = funasr_response.json()

print("Whisper:", whisper_result["text"])
print("FunASR:", funasr_result["text"])
print()

# 5. Endpoint simples
print("=== Endpoint Simples ===")
with open("audio.mp3", "rb") as f:
    response = requests.post(
        f"{API_URL}/transcribe-simple",
        files={"file": f},
        data={"engine": "funasr"}  # ou "whisper"
    )
    print(response.json())
