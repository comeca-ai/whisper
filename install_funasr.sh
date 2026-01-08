#!/bin/bash

echo "=== Instalando FunASR para usar com a API ==="

# Instalar FunASR e dependências
pip install funasr modelscope

# Opcional: Instalar onnxruntime para melhor performance
pip install onnxruntime

echo ""
echo "✅ FunASR instalado com sucesso!"
echo ""
echo "Modelos disponíveis:"
echo "  - paraformer-zh: Melhor para chinês"
echo "  - paraformer-en: Melhor para inglês"
echo "  - paraformer-large-v2: Modelo grande multilíngue"
echo ""
echo "Para iniciar a API:"
echo "  python api.py"
echo ""
