#!/bin/bash

echo "=== Teste da API Multi-Engine ==="
echo ""

# 1. Health Check
echo "1. Health Check:"
curl -s http://localhost:8000/health | jq
echo ""

# 2. Listar modelos disponíveis
echo "2. Modelos Disponíveis:"
curl -s http://localhost:8000/models | jq
echo ""

# 3. Teste com JFK (inglês)
echo "3. Teste JFK - Whisper Tiny:"
curl -s -X POST "http://localhost:8000/transcribe" \
  -F "file=@tests/jfk.flac" \
  -F "engine=whisper" \
  -F "model=tiny" | jq -r '.text'
echo ""

echo "4. Teste JFK - Whisper Base:"
curl -s -X POST "http://localhost:8000/transcribe" \
  -F "file=@tests/jfk.flac" \
  -F "engine=whisper" \
  -F "model=base" | jq -r '.text'
echo ""

# 5. Teste com áudio em português
if [ -f "WhatsApp Audio 2025-12-31 at 21.12.07.ogg" ]; then
  echo "5. Teste Áudio PT-BR - Whisper Base:"
  curl -s -X POST "http://localhost:8000/transcribe" \
    -F "file=@WhatsApp Audio 2025-12-31 at 21.12.07.ogg" \
    -F "engine=whisper" \
    -F "model=base" \
    -F "language=pt" | jq -r '.text'
  echo ""
  
  echo "6. Teste Áudio PT-BR - Whisper Small:"
  curl -s -X POST "http://localhost:8000/transcribe" \
    -F "file=@WhatsApp Audio 2025-12-31 at 21.12.07.ogg" \
    -F "engine=whisper" \
    -F "model=small" \
    -F "language=pt" | jq -r '.text'
  echo ""
fi

# 7. Endpoint simples
echo "7. Teste Endpoint Simples:"
curl -s -X POST "http://localhost:8000/transcribe-simple" \
  -F "file=@tests/jfk.flac" \
  -F "engine=whisper" | jq -r '.text'
echo ""

echo "=== Testes Concluídos! ==="
