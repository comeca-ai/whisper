"""
API aprimorada com parâmetros para reduzir repetições e palavras inventadas
Railway-ready with environment variables support
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
import re
from typing import Optional, Union, List
import logging

# Railway environment configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8001))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 26214400))  # 25MB default
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Whisper API Otimizada - Railway Ready",
    description="API com parâmetros otimizados para reduzir repetições e palavras inventadas",
    version="3.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for loaded models
model_cache = {}

# Glossário para correções comuns
CORRECTION_GLOSSARY = {
    'bereg': 'Derek',
    'berek': 'Derek',
    'dreta': 'ideia',
    'chau': 'show',
    'becanismo': 'mecanismo',
    'fetalóxico': 'Fitalóxica',
    'fetalóx': 'Fitalóxica',
    'fita-lóxica': 'Fitalóxica',
    'orto': 'Arthur',
    'johnathan': 'Jonathan',
    'bacténea': 'bactéria',
    'maestônia': 'mecenato',
    'dore': 'doré'
}

def get_model(model_size: str):
    """Load and cache Whisper model."""
    if model_size not in model_cache:
        logger.info(f"Loading Whisper model: {model_size}")
        model_cache[model_size] = whisper.load_model(model_size)
    return model_cache[model_size]

def clean_repetitions(text: str) -> str:
    """Remove repetições excessivas do texto."""
    if not text:
        return text
        
    # Remove repetições massivas de conectivos
    text = re.sub(r'(\be, e, e,? ){3,}e?', 'e ', text)
    text = re.sub(r'(\be e ){3,}', 'e ', text)
    
    # Remove repetições de palavras técnicas
    text = re.sub(r'(\b\w+)(?:,? a \1){3,}', r'\1', text)
    text = re.sub(r'(\b\w+)(?:, \1){3,}', r'\1', text)
    
    # Remove sequências repetitivas no final (padrão comum do Whisper)
    text = re.sub(r'(\b\w+)(?:, \1){10,}.*$', r'\1.', text)
    
    # Limpar espaços múltiplos
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def apply_corrections(text: str) -> str:
    """Aplicar correções do glossário."""
    if not text:
        return text
        
    words = text.split()
    corrected_words = []
    
    for word in words:
        # Remove pontuação para comparação
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        if clean_word in CORRECTION_GLOSSARY:
            # Preservar pontuação original
            original_punct = re.findall(r'[^\w]', word)
            corrected = CORRECTION_GLOSSARY[clean_word]
            if original_punct:
                corrected += ''.join(original_punct)
            corrected_words.append(corrected)
        else:
            corrected_words.append(word)
    
    return ' '.join(corrected_words)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "3.0.0"}

@app.get("/models")
async def list_models():
    """List available models and optimization features."""
    return {
        "whisper_models": ["tiny", "base", "small", "medium", "large", "turbo"],
        "optimizations": {
            "anti_repetition": True,
            "glossary_correction": True,
            "advanced_parameters": True
        },
        "loaded_models": list(model_cache.keys())
    }

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = Form("base", description="Whisper model to use"),
    language: Optional[str] = Form(None, description="Force language (e.g., 'pt')"),
    
    # Parâmetros anti-repetição
    temperature: float = Form(0.0, description="Temperature (0.0 = mais determinístico)"),
    compression_ratio_threshold: float = Form(2.4, description="Limite para detectar repetições"),
    logprob_threshold: float = Form(-1.0, description="Limite de probabilidade logarítmica"),
    no_speech_threshold: float = Form(0.6, description="Limite para detectar silêncio"),
    condition_on_previous_text: bool = Form(True, description="Usar contexto anterior"),
    
    # Parâmetros de qualidade
    initial_prompt: Optional[str] = Form(None, description="Prompt inicial para guiar a transcrição"),
    
    # Configurações de pós-processamento
    apply_corrections: bool = Form(True, description="Aplicar correções do glossário"),
    clean_repetitions: bool = Form(True, description="Limpar repetições excessivas"),
    
    # Configuração de robustez
    use_multiple_temperatures: bool = Form(True, description="Usar múltiplas temperaturas para melhor qualidade")
):
    """
    Transcrever áudio com parâmetros otimizados para reduzir repetições e palavras inventadas.
    
    **Parâmetros anti-repetição:**
    - **temperature**: 0.0 = mais determinístico (menos repetições)
    - **compression_ratio_threshold**: Detecta repetições (padrão: 2.4)
    - **condition_on_previous_text**: False reduz dependência de contexto ruim
    
    **Melhorias:**
    - Limpeza automática de repetições excessivas
    - Glossário de correções para palavras comuns
    - Múltiplas temperaturas para maior robustez
    """
    
    logger.info(f"Transcribing with model: {model}, optimizations enabled")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Load model with environment default
        model_name = model or os.getenv('WHISPER_MODEL', 'base')
        whisper_model = get_model(model_name)
        
        # Configurar temperaturas múltiplas para maior robustez
        if use_multiple_temperatures:
            temperatures = (0.0, 0.2, 0.4) if temperature == 0.0 else (temperature,)
        else:
            temperatures = (temperature,)
        
        # Configurar prompt inicial se não fornecido
        if initial_prompt is None:
            initial_prompt = "Esta é uma transcrição de áudio em português brasileiro. Fale com clareza e evite repetições."
        
        # Parâmetros otimizados com environment variables defaults
        compression_ratio_threshold = compression_ratio_threshold if compression_ratio_threshold is not None else float(os.getenv('COMPRESSION_RATIO_THRESHOLD', 1.8))
        condition_on_previous_text = condition_on_previous_text if condition_on_previous_text is not None else os.getenv('CONDITION_ON_PREVIOUS_TEXT', 'false').lower() != 'false'
        
        transcription_options = {
            "language": language,
            "temperature": temperatures,
            "compression_ratio_threshold": compression_ratio_threshold,
            "logprob_threshold": logprob_threshold, 
            "no_speech_threshold": no_speech_threshold,
            "condition_on_previous_text": condition_on_previous_text,
            "initial_prompt": initial_prompt,
            "verbose": False,
            "word_timestamps": True  # Ajuda na qualidade
        }
        
        logger.info(f"Transcription options: {transcription_options}")
        
        # Executar transcrição
        result = whisper_model.transcribe(temp_file_path, **transcription_options)
        
        # Pós-processamento
        transcribed_text = result["text"]
        original_text = transcribed_text
        
        # Aplicar otimizações baseadas em environment variables
        clean_repetitions_flag = clean_repetitions if clean_repetitions is not None else os.getenv('CLEAN_REPETITIONS', 'true').lower() != 'false'
        apply_corrections_flag = apply_corrections if apply_corrections is not None else os.getenv('APPLY_CORRECTIONS', 'true').lower() != 'false'
        
        if clean_repetitions_flag:
            transcribed_text = globals()['clean_repetitions'](transcribed_text)
            
        if apply_corrections_flag:
            transcribed_text = globals()['apply_corrections'](transcribed_text)
        
        # Preparar resposta
        response = {
            "engine": "whisper",
            "model": model_name,
            "text": transcribed_text,
            "original_text": original_text,  # Manter original para comparação
            "language": result.get("language"),
            "optimizations_applied": {
                "repetitions_cleaned": clean_repetitions_flag,
                "corrections_applied": apply_corrections_flag,
                "multiple_temperatures": use_multiple_temperatures
            },
            "segments": [
                {
                    "id": seg["id"],
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result.get("segments", [])
            ]
        }
        
        logger.info("Transcription completed successfully with optimizations")
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    finally:
        # Clean up temp file
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass

@app.post("/add_correction")
async def add_correction(
    wrong_word: str = Form(..., description="Palavra incorreta"),
    correct_word: str = Form(..., description="Palavra correta")
):
    """Adicionar nova correção ao glossário."""
    CORRECTION_GLOSSARY[wrong_word.lower()] = correct_word
    return {
        "message": f"Correção adicionada: {wrong_word} -> {correct_word}",
        "total_corrections": len(CORRECTION_GLOSSARY)
    }

@app.get("/corrections")
async def get_corrections():
    """Listar todas as correções disponíveis."""
    return {
        "glossary": CORRECTION_GLOSSARY,
        "total": len(CORRECTION_GLOSSARY)
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Starting Whisper Enhanced API on {HOST}:{PORT}")
    logger.info(f"🎯 Default model: {os.getenv('WHISPER_MODEL', 'base')}")
    logger.info(f"🧹 Clean repetitions: {os.getenv('CLEAN_REPETITIONS', 'true')}")
    uvicorn.run(app, host=HOST, port=PORT)