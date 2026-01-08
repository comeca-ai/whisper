# Whisper Enhanced

[[Blog]](https://openai.com/blog/whisper)
[[Paper]](https://arxiv.org/abs/2212.04356)
[[Model card]](https://github.com/openai/whisper/blob/main/model-card.md)
[[Colab example]](https://colab.research.google.com/github/openai/whisper/blob/master/notebooks/LibriSpeech.ipynb)

Whisper is a general-purpose speech recognition model. It is trained on a large dataset of diverse audio and is also a multitasking model that can perform multilingual speech recognition, speech translation, and language identification.

## ⚡ Enhanced Features

This repository includes **optimized APIs** and **comprehensive testing tools** for production use:

- 🚀 **Optimized API** with anti-repetition parameters
- 🔧 **Multiple engines** (Whisper, Faster-Whisper, FunASR, Wav2Vec2)  
- 🎯 **Automatic correction** of invented words
- 📊 **Comprehensive performance testing**
- 🧹 **Automatic repetition cleanup**

## 🏆 Performance Results

Based on comprehensive testing with Portuguese WhatsApp audio files:

| Model | Speed | Accuracy | Repetition Issues | Recommendation |
|-------|--------|----------|------------------|----------------|
| **Whisper Base** | 6.20s avg | 100% success | ✅ Minimal (2 errors) | 🥇 **Best for Production** |
| **Whisper Tiny** | 4.66s avg | 100% success | ❌ Significant (45 errors) | ⚡ Fast but needs optimization |
| **Whisper Tiny + Optimizations** | 4.66s avg | 100% success | ✅ **Eliminated** | 🚀 **Best Performance/Speed** |

> **📊 Full test results:** [Performance Report](docs/RELATORIO_TESTE_MODELOS.md)

## 🚀 Quick Start

### 1. Basic Installation

```bash
pip install -U openai-whisper
```

### 2. Enhanced API Installation

```bash
pip install -r requirements-api.txt
```

### 3. Start Optimized API

```bash
# Standard API (port 8000)
python api.py

# Optimized API with anti-repetition (port 8001) - RECOMMENDED
python api_otimizada.py
```

## 📡 API Usage

### Standard Transcription
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base"
```

### 🔥 Optimized Transcription (Recommended)
```bash
curl -X POST "http://localhost:8001/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "compression_ratio_threshold=1.8" \
  -F "condition_on_previous_text=false" \
  -F "clean_repetitions=true" \
  -F "apply_corrections=true"
```

## 🎯 Key Optimization Parameters

| Parameter | Default | Optimized | Impact |
|-----------|---------|-----------|---------|
| `compression_ratio_threshold` | 2.4 | **1.8** | 🔥 Detects repetitions earlier |
| `condition_on_previous_text` | True | **False** | 🛑 Prevents error propagation |
| `clean_repetitions` | N/A | **True** | 🧹 Automatic cleanup |
| `apply_corrections` | N/A | **True** | 📚 Word correction glossary |

## 🧪 Testing & Validation

### Run Comprehensive Tests
```bash
# Test all models with your audio files
python scripts/teste_estrategico_final.py

# Compare original vs optimized API
python scripts/demo_melhorias.py

# Analyze transcription errors
python scripts/analise_erros.py
```

### Sample Test Results
- ✅ **100% success rate** across 18 tests
- ✅ **Portuguese detection**: Perfect accuracy
- ✅ **Repetition elimination**: 95%+ improvement
- ✅ **Speed maintained**: Optimizations don't slow down processing

## 📁 Project Structure

```
whisper/
├── api.py                    # Standard multi-engine API
├── api_otimizada.py         # ✨ Optimized API (RECOMMENDED)
├── scripts/                 # Testing and analysis tools
│   ├── teste_estrategico_final.py
│   ├── demo_melhorias.py
│   ├── analise_erros.py
│   └── ...
├── docs/                    # Documentation
│   ├── RELATORIO_TESTE_MODELOS.md
│   ├── ANALISE_ERROS_DETALHADA.md
│   ├── GUIA_OTIMIZACOES.md
│   └── ...
├── results/                 # Test results and reports
├── audios/                  # Sample audio files
└── requirements-api.txt     # API dependencies
```

## 🔧 Advanced Configuration

### For Maximum Quality (Production)
```python
{
    "model": "base",
    "temperature": 0.0,
    "compression_ratio_threshold": 1.6,  # Very strict
    "condition_on_previous_text": False,
    "clean_repetitions": True,
    "apply_corrections": True
}
```

### For Speed with Quality
```python
{
    "model": "tiny",
    "compression_ratio_threshold": 2.0,
    "condition_on_previous_text": False,
    "clean_repetitions": True,  # ESSENTIAL for tiny model
    "apply_corrections": True
}
```

## 🏆 Benchmark Results

### Problem Resolution
- **Before**: 108 repetition errors, unusable transcripts
- **After**: 0 repetition errors, clean professional output

### Example Improvement
```
❌ Before: "...e, e, e, e, e, e, e, e, e, e, e, e, e, e, e, e..."
✅ After:  "...e manda notícia aí, abração."
```

## 📚 Documentation

- 📊 [Performance Testing Report](docs/RELATORIO_TESTE_MODELOS.md)
- 🔍 [Error Analysis](docs/ANALISE_ERROS_DETALHADA.md) 
- 🚀 [Optimization Guide](docs/GUIA_OTIMIZACOES.md)
- 📡 [API Documentation](docs/README_API.md)
- 🔧 [Multi-Engine Setup](docs/README_MULTI_ENGINE.md)

## 🔧 Original Whisper Setup

We used Python 3.9.9 and [PyTorch](https://pytorch.org/) 1.10.1 to train and test our models, but the codebase is expected to be compatible with Python 3.8-3.11 and recent PyTorch versions. The codebase also depends on a few Python packages, most notably [OpenAI's tiktoken](https://github.com/openai/tiktoken) for their fast tokenizer implementation. 

### Standard Installation
```bash
pip install -U openai-whisper
```

Alternatively, from repository:
```bash
pip install git+https://github.com/openai/whisper.git 
```

### FFmpeg Installation
```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```

## Available models and languages

There are five model sizes, four of which have English-only versions, offering speed and accuracy tradeoffs. Below are the names of the available models and their approximate memory requirements and relative speed.

|  Size  | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed |
|:------:|:----------:|:------------------:|:------------------:|:-------------:|:--------------:|
|  tiny  |    39 M    |     `tiny.en`     |       `tiny`       |     ~1 GB     |      ~32x      |
|  base  |    74 M    |     `base.en`     |       `base`       |     ~1 GB     |      ~16x      |
| small  |   244 M    |    `small.en`     |      `small`       |     ~2 GB     |      ~6x       |
| medium |   769 M    |   `medium.en`     |      `medium`      |     ~5 GB     |      ~2x       |
| large  |   1550 M   |        N/A         |      `large`       |    ~10 GB     |       1x       |

The `.en` models are English-only and tend to perform better on English speech but cannot transcribe other languages, while the regular models are multilingual.

For English speech recognition, the `.en` models tend to perform better, especially for the `tiny.en` and `base.en` models. We observed that the difference becomes less significant for the `small.en` and `medium.en` models.

See the [model card](https://github.com/openai/whisper/blob/main/model-card.md) for more details on what to expect for each model size.

## 🤝 Contributing

This enhanced version includes comprehensive testing and optimization features. To contribute:

1. Test your changes with the provided test scripts
2. Update documentation in the `docs/` folder  
3. Ensure optimized API maintains compatibility

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.