# API Multi-Engine de Transcrição de Áudio

Esta API suporta múltiplos motores de transcrição:
- **Whisper** (OpenAI) - Excelente para múltiplos idiomas
- **FunASR** (Alibaba) - Rápido e eficiente, ótimo para chinês

## Instalação

### Básico (apenas Whisper)
```bash
pip install -r requirements-api.txt
```

### Com FunASR
```bash
pip install -r requirements-api.txt
pip install funasr modelscope
# ou
bash install_funasr.sh
```

## Uso

### Iniciar API
```bash
python api.py
# ou
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints

#### 1. Listar modelos disponíveis
```bash
curl http://localhost:8000/models
```

Resposta:
```json
{
  "engines": ["whisper", "funasr"],
  "whisper_models": ["tiny", "base", "small", "medium", "large", "turbo"],
  "funasr_models": ["paraformer-zh", "paraformer-en", "paraformer-large-v2"],
  "loaded_whisper": [],
  "loaded_funasr": [],
  "funasr_available": true
}
```

#### 2. Transcrever com Whisper
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "engine=whisper" \
  -F "model=base" \
  -F "language=pt"
```

#### 3. Transcrever com FunASR
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "engine=funasr" \
  -F "model=paraformer-zh"
```

#### 4. Endpoint simples
```bash
curl -X POST "http://localhost:8000/transcribe-simple" \
  -F "file=@audio.mp3" \
  -F "engine=whisper"
```

### Python

```python
import requests

# Com Whisper
with open("audio.mp3", "rb") as f:
    response = requests.post(
        "http://localhost:8000/transcribe",
        files={"file": f},
        data={
            "engine": "whisper",
            "model": "base",
            "language": "pt"
        }
    )
    print(response.json()["text"])

# Com FunASR
with open("audio.mp3", "rb") as f:
    response = requests.post(
        "http://localhost:8000/transcribe",
        files={"file": f},
        data={
            "engine": "funasr",
            "model": "paraformer-large-v2"
        }
    )
    print(response.json()["text"])
```

### JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('audio.mp3'));
form.append('engine', 'whisper');
form.append('model', 'base');

fetch('http://localhost:8000/transcribe', {
    method: 'POST',
    body: form
})
.then(res => res.json())
.then(data => console.log(data.text));
```

## Comparação de Modelos

### Whisper

| Modelo | Parâmetros | VRAM | Velocidade | Melhor para |
|--------|------------|------|------------|-------------|
| tiny | 39M | ~1 GB | 10x | Testes rápidos |
| base | 74M | ~1 GB | 7x | Uso geral |
| small | 244M | ~2 GB | 4x | Boa precisão |
| medium | 769M | ~5 GB | 2x | Alta precisão |
| large | 1550M | ~10 GB | 1x | Máxima precisão |
| turbo | 809M | ~6 GB | 8x | Rápido + preciso |

**Idiomas**: 90+ idiomas incluindo português, inglês, espanhol, chinês, etc.

### FunASR

| Modelo | Melhor para | Velocidade | Precisão |
|--------|-------------|------------|----------|
| paraformer-zh | Chinês | Muito rápida | Excelente |
| paraformer-en | Inglês | Muito rápida | Excelente |
| paraformer-large-v2 | Multilíngue | Rápida | Excelente |

**Idiomas**: Principalmente chinês e inglês.

## Quando usar cada motor?

### Use Whisper quando:
- Precisar de suporte a múltiplos idiomas (90+)
- Português brasileiro for o idioma principal
- Precisar traduzir para inglês
- Precisar de timestamps precisos por palavra

### Use FunASR quando:
- Áudio estiver em chinês (melhor performance)
- Áudio estiver em inglês e velocidade for crítica
- Tiver recursos limitados (mais eficiente)
- Precisar de baixa latência

## Resposta da API

```json
{
  "engine": "whisper",
  "model": "base",
  "text": "Texto transcrito completo",
  "language": "pt",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Primeiro segmento"
    },
    {
      "id": 1,
      "start": 3.5,
      "end": 7.2,
      "text": "Segundo segmento"
    }
  ]
}
```

## Performance

Para melhorar a performance:

1. **Cache de modelos**: Modelos são carregados uma vez e mantidos em memória
2. **GPU**: Whisper e FunASR usam GPU automaticamente se disponível
3. **Modelos menores**: Use `tiny` ou `base` para respostas mais rápidas
4. **FunASR**: Geralmente 2-4x mais rápido que Whisper equivalente

## Troubleshooting

### FunASR não está disponível
```bash
pip install funasr modelscope
```

### Erro de memória
- Use modelos menores: `tiny`, `base` para Whisper
- Use `paraformer-en` ou `paraformer-zh` para FunASR

### GPU não detectada
- Instale CUDA/cuDNN compatível
- Reinstale PyTorch com suporte CUDA

## Docs da API

Acesse a documentação interativa:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
