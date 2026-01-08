#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🎵 TESTE COMPARATIVO - 2 ÁUDIOS | TODOS OS MODELOS         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Áudios
AUDIO1="tests/jfk.flac"
AUDIO2="WhatsApp Audio 2025-12-31 at 21.12.07.ogg"

# Função para testar
test_audio() {
    local audio=$1
    local engine=$2
    local model=$3
    local lang=$4
    
    RESULT=$(curl -s -X POST "http://localhost:8000/transcribe" \
        -F "file=@$audio" \
        -F "engine=$engine" \
        -F "model=$model" \
        -F "language=$lang" 2>&1)
    
    if echo "$RESULT" | jq -e '.text' > /dev/null 2>&1; then
        echo "$RESULT" | jq -r '.text'
    else
        echo "❌ ERRO"
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 ÁUDIO 1: JFK Speech (Inglês)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔹 Whisper Tiny:"
test_audio "$AUDIO1" "whisper" "tiny" ""
echo ""

echo "🔹 Whisper Base:"
test_audio "$AUDIO1" "whisper" "base" ""
echo ""

echo "🔹 Faster Whisper Tiny:"
test_audio "$AUDIO1" "faster-whisper" "tiny" ""
echo ""

echo "🔹 Faster Whisper Base:"
test_audio "$AUDIO1" "faster-whisper" "base" ""
echo ""

echo "🔹 Faster Whisper Small:"
test_audio "$AUDIO1" "faster-whisper" "small" ""
echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 ÁUDIO 2: WhatsApp (Português BR)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔹 Whisper Tiny (PT):"
test_audio "$AUDIO2" "whisper" "tiny" "pt"
echo ""

echo "🔹 Whisper Base (PT):"
test_audio "$AUDIO2" "whisper" "base" "pt"
echo ""

echo "🔹 Whisper Small (PT):"
test_audio "$AUDIO2" "whisper" "small" "pt"
echo ""

echo "🔹 Faster Whisper Tiny (PT):"
test_audio "$AUDIO2" "faster-whisper" "tiny" "pt"
echo ""

echo "🔹 Faster Whisper Base (PT):"
test_audio "$AUDIO2" "faster-whisper" "base" "pt"
echo ""

echo "🔹 Faster Whisper Small (PT):"
test_audio "$AUDIO2" "faster-whisper" "small" "pt"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TESTES CONCLUÍDOS!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
