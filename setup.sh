#!/bin/bash

# =============================================================================
# WHISPER ENHANCED - SETUP E CONFIGURAÇÃO PRINCIPAL
# =============================================================================

echo "🚀 Whisper Enhanced - Configuração Automática"
echo "=============================================="

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

# Instala dependências principais
echo "📦 Instalando dependências principais..."
pip install -r requirements.txt

# Instala dependências da API
echo "📡 Instalando dependências da API..."
pip install -r requirements-api.txt

# Verifica FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ FFmpeg não encontrado. Tentando instalar..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y ffmpeg
    elif command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Por favor, instale FFmpeg manualmente"
        exit 1
    fi
fi

# Cria diretórios necessários
echo "📁 Criando estrutura de diretórios..."
mkdir -p audios results logs

# Baixa modelo padrão (base)
echo "🤖 Baixando modelo Whisper base..."
python -c "import whisper; whisper.load_model('base')" 

echo ""
echo "✅ Configuração concluída com sucesso!"
echo ""
echo "🔥 PRÓXIMOS PASSOS:"
echo "==================="
echo ""
echo "1️⃣ INICIE A API OTIMIZADA (RECOMENDADO):"
echo "   python api_otimizada.py"
echo ""
echo "2️⃣ OU API MULTI-ENGINE:"
echo "   python api.py"
echo ""
echo "3️⃣ TESTE A API:"
echo "   curl -X POST \"http://localhost:8001/transcribe\" \\"
echo "     -F \"file=@seu_audio.mp3\" \\"
echo "     -F \"model=base\" \\"
echo "     -F \"clean_repetitions=true\""
echo ""
echo "4️⃣ EXECUTE TESTES COMPLETOS:"
echo "   python scripts/teste_estrategico_final.py"
echo ""
echo "📚 DOCUMENTAÇÃO COMPLETA:"
echo "   - docs/PROJETO_FINAL_DOCUMENTACAO.md"
echo "   - docs/GUIA_OTIMIZACOES.md" 
echo "   - docs/README_API.md"
echo ""
echo "🎯 CONFIGURAÇÃO RECOMENDADA PARA PRODUÇÃO:"
echo "   Modelo: base"
echo "   compression_ratio_threshold: 1.8"
echo "   condition_on_previous_text: false"
echo "   clean_repetitions: true"
echo ""