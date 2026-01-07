# Whisper FastAPI Endpoint

API REST para transcrição de áudio usando OpenAI Whisper.

## 🚀 Início Rápido

### Instalação

```bash
# Instalar dependências da API
pip install -r requirements-api.txt
```

### Executar o servidor

```bash
# Desenvolvimento (com reload automático)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

O servidor estará disponível em: `http://localhost:8000`

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 Endpoints

### GET `/`
Informações sobre a API.

### GET `/health`
Health check do serviço.

### GET `/models`
Lista os modelos Whisper disponíveis.

### POST `/transcribe`
Transcreve um arquivo de áudio.

**Parâmetros:**
- `file` (obrigatório): Arquivo de áudio (mp3, wav, m4a, etc.)
- `model` (opcional): Tamanho do modelo (`tiny`, `base`, `small`, `medium`, `large`)
- `language` (opcional): Código do idioma (ex: `pt`, `en`)
- `task` (opcional): `transcribe` ou `translate`
- `temperature` (opcional): Temperatura de amostragem (padrão: 0.0)
- `verbose` (opcional): Habilitar saída detalhada

**Exemplo usando curl:**

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "language=pt"
```

**Exemplo usando Python:**

```python
import requests

with open('audio.mp3', 'rb') as f:
    files = {'file': f}
    data = {'model': 'base', 'language': 'pt'}
    response = requests.post('http://localhost:8000/transcribe', 
                           files=files, data=data)
    
print(response.json()['text'])
```

### POST `/transcribe-simple`
Endpoint simplificado para transcrição rápida (usa configurações padrão).

**Parâmetros:**
- `file` (obrigatório): Arquivo de áudio

## 🐳 Docker

### Build e execução

```bash
# Build da imagem
docker build -t whisper-api .

# Executar container
docker run -p 8000:8000 whisper-api
```

### Usando Docker Compose

```bash
docker-compose up
```

## 🧪 Testes

```bash
# Testar a API com um arquivo de áudio
python test_api.py caminho/para/audio.mp3
```

## 📊 Modelos Disponíveis

| Modelo | Parâmetros | Memória VRAM | Velocidade Relativa |
|--------|-----------|--------------|---------------------|
| tiny   | 39 M      | ~1 GB        | ~32x                |
| base   | 74 M      | ~1 GB        | ~16x                |
| small  | 244 M     | ~2 GB        | ~6x                 |
| medium | 769 M     | ~5 GB        | ~2x                 |
| large  | 1550 M    | ~10 GB       | 1x                  |

## 🌐 Formatos de Áudio Suportados

A API suporta qualquer formato que o FFmpeg consiga processar:
- MP3
- WAV
- M4A
- FLAC
- OGG
- AAC
- WMA
- E muitos outros...

## ⚙️ Variáveis de Ambiente

```bash
# Opcional: configurar device (cpu ou cuda)
export WHISPER_DEVICE=cpu

# Opcional: diretório de cache dos modelos
export WHISPER_CACHE_DIR=/caminho/para/cache
```

## 📝 Resposta da API

```json
{
  "text": "Texto completo transcrito do áudio.",
  "language": "pt",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Primeiro segmento do áudio."
    },
    {
      "id": 1,
      "start": 3.5,
      "end": 7.2,
      "text": "Segundo segmento do áudio."
    }
  ]
}
```

## 🔒 Segurança

Para produção, considere:
- Limitar o tamanho máximo de upload
- Adicionar autenticação (API key, OAuth, etc.)
- Configurar rate limiting
- Usar HTTPS
- Validar tipos de arquivo

## 📈 Performance

Para melhorar a performance:
- Use GPU quando disponível (CUDA)
- Ajuste o número de workers do uvicorn
- Considere usar modelos menores (tiny/base) para transcrições rápidas
- Implemente cache de resultados para arquivos frequentes
- Use async workers

## 🐛 Solução de Problemas

### Erro: "Could not load library cudnn_cnn_infer64_8.dll"
- Execute com CPU: configure a variável de ambiente `WHISPER_DEVICE=cpu`

### Erro: "ffmpeg not found"
- Instale ffmpeg: `apt-get install ffmpeg` (Linux) ou `brew install ffmpeg` (Mac)

### API lenta
- Use modelo menor (tiny ou base)
- Verifique se está usando GPU
- Aumente o número de workers
