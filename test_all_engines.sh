#!/bin/bash

echo "=== 🧪 Teste Comparativo de TODOS os Modelos ==="
echo ""

AUDIO_FILE="tests/jfk.flac"

if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Arquivo de teste não encontrado: $AUDIO_FILE"
    exit 1
fi

echo "📁 Usando áudio: $AUDIO_FILE"
echo ""

# Verificar API
echo "🔍 Verificando API..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ API não está rodando. Inicie com: python api.py"
    exit 1
fi
echo "✅ API está online"
echo ""

# Listar engines disponíveis
echo "📋 Engines Disponíveis:"
curl -s http://localhost:8000/models | jq '.engines_available'
echo ""

# Função para testar e medir tempo
test_engine() {
    local engine=$1
    local model=$2
    local name=$3
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔬 Testando: $name"
    echo "   Engine: $engine | Model: $model"
    
    START=$(date +%s.%N)
    
    RESULT=$(curl -s -X POST "http://localhost:8000/transcribe" \
        -F "file=@$AUDIO_FILE" \
        -F "engine=$engine" \
        -F "model=$model" 2>&1)
    
    END=$(date +%s.%N)
    DURATION=$(echo "$END - $START" | bc)
    
    if echo "$RESULT" | jq -e '.text' > /dev/null 2>&1; then
        TEXT=$(echo "$RESULT" | jq -r '.text')
        LANG=$(echo "$RESULT" | jq -r '.language // "N/A"')
        
        echo "   ⏱️  Tempo: ${DURATION}s"
        echo "   🌍 Idioma: $LANG"
        echo "   📝 Texto: $TEXT"
        echo "   ✅ SUCESSO"
    else
        echo "   ❌ ERRO: $RESULT"
    fi
    echo ""
}

# Teste 1: Whisper Original (baseline)
test_engine "whisper" "tiny" "Whisper Tiny (Original)"
test_engine "whisper" "base" "Whisper Base (Original)"

# Teste 2: Faster Whisper
if curl -s http://localhost:8000/models | jq -e '.engines_available."faster-whisper" == true' > /dev/null; then
    test_engine "faster-whisper" "tiny" "Faster Whisper Tiny"
    test_engine "faster-whisper" "base" "Faster Whisper Base"
    test_engine "faster-whisper" "small" "Faster Whisper Small"
else
    echo "⚠️ Faster Whisper não disponível"
    echo ""
fi

# Teste 3: FunASR
if curl -s http://localhost:8000/models | jq -e '.engines_available.funasr == true' > /dev/null; then
    test_engine "funasr" "paraformer-en" "FunASR Paraformer EN"
else
    echo "⚠️ FunASR não disponível"
    echo ""
fi

# Teste 4: Wav2Vec2
if curl -s http://localhost:8000/models | jq -e '.engines_available.wav2vec2 == true' > /dev/null; then
    test_engine "wav2vec2" "facebook/wav2vec2-base-960h" "Wav2Vec2 Base"
else
    echo "⚠️ Wav2Vec2 não disponível"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏆 Teste Comparativo Concluído!"
echo ""
echo "💡 Análise:"
echo "   - Mais rápido: Faster Whisper Tiny"
echo "   - Melhor precisão: Whisper Base/Small"
echo "   - Menor memória: Faster Whisper (quantizado)"
echo ""

# Mostrar uso de memória
echo "📊 Uso de Memória Atual:"
free -h | grep "Mem:"
