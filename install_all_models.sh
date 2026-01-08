#!/bin/bash

echo "=== Instalando Todos os Modelos de Transcrição ==="
echo ""

# Verificar recursos
echo "📊 Recursos da máquina:"
free -h | grep "Mem:"
echo ""

# 1. Faster Whisper (RECOMENDADO - mais leve e rápido)
echo "1️⃣ Instalando Faster Whisper..."
pip install -q faster-whisper
if [ $? -eq 0 ]; then
    echo "✅ Faster Whisper instalado"
else
    echo "❌ Erro ao instalar Faster Whisper"
fi
echo ""

# 2. FunASR (Alibaba - opcional)
echo "2️⃣ Instalando FunASR (Alibaba)..."
pip install -q funasr modelscope
if [ $? -eq 0 ]; then
    echo "✅ FunASR instalado"
else
    echo "❌ Erro ao instalar FunASR"
fi
echo ""

# 3. Transformers + Wav2Vec2 (apenas se tiver memória)
echo "3️⃣ Instalando Transformers (Wav2Vec2)..."
MEM_AVAILABLE=$(free -g | awk '/^Mem:/{print $7}')
if [ "$MEM_AVAILABLE" -gt 2 ]; then
    pip install -q transformers torch torchaudio librosa
    if [ $? -eq 0 ]; then
        echo "✅ Transformers instalado"
    else
        echo "❌ Erro ao instalar Transformers"
    fi
else
    echo "⚠️ Memória insuficiente ($MEM_AVAILABLE GB livre). Pulando Transformers."
fi
echo ""

echo "=== Resumo da Instalação ==="
echo ""
echo "Engines disponíveis:"
python3 -c "
try:
    import faster_whisper
    print('✅ Faster Whisper')
except:
    print('❌ Faster Whisper')
    
try:
    import funasr
    print('✅ FunASR')
except:
    print('❌ FunASR')
    
try:
    import transformers
    print('✅ Transformers (Wav2Vec2)')
except:
    print('❌ Transformers')

import whisper
print('✅ Whisper (original)')
"

echo ""
echo "🚀 Para testar, execute:"
echo "   python api.py"
echo ""
