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
from openrouter_integration import openrouter_client

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
    """Health check endpoint with OpenRouter integration status."""
    openrouter_status = "enabled" if openrouter_client.api_key else "disabled"
    
    return {
        "status": "healthy", 
        "version": "3.1.0",
        "features": {
            "whisper_optimization": "enabled",
            "openrouter_integration": openrouter_status,
            "ai_features": ["summarize", "translate", "sentiment", "improve"]
        },
        "models": ["tiny", "base", "small", "medium", "large", "turbo"]
    }

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

# ============================================================================
# OPENROUTER INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/transcribe-and-summarize")
async def transcribe_and_summarize(
    file: UploadFile = File(...),
    model: str = Form(None),
    language: str = Form("pt"),
    summary_length: str = Form("short")  # short, medium, long
):
    """Transcribe audio and generate AI summary."""
    
    # First transcribe
    transcribe_result = await transcribe_optimized(
        file=file,
        model=model,
        language=language,
        clean_repetitions=True,
        apply_corrections=True
    )
    
    if "error" in transcribe_result:
        return transcribe_result
    
    # Then summarize
    try:
        summary = await openrouter_client.summarize_text(transcribe_result["text"])
        
        return {
            "transcription": transcribe_result,
            "summary": summary,
            "processing": {
                "transcription_engine": "whisper",
                "ai_model": "claude-3.5-sonnet",
                "summary_length": summary_length
            }
        }
        
    except Exception as e:
        return {
            "transcription": transcribe_result,
            "summary_error": str(e),
            "message": "Transcription succeeded but summary failed"
        }

@app.post("/transcribe-and-translate")
async def transcribe_and_translate(
    file: UploadFile = File(...),
    model: str = Form(None),
    target_language: str = Form("en"),  # en, es, fr, de, it
    language: str = Form("pt")
):
    """Transcribe audio and translate to target language."""
    
    # First transcribe
    transcribe_result = await transcribe_optimized(
        file=file,
        model=model,
        language=language,
        clean_repetitions=True,
        apply_corrections=True
    )
    
    if "error" in transcribe_result:
        return transcribe_result
    
    # Then translate
    try:
        translation = await openrouter_client.translate_text(
            transcribe_result["text"], 
            target_language
        )
        
        return {
            "original_transcription": transcribe_result,
            "translation": {
                "text": translation,
                "target_language": target_language
            },
            "processing": {
                "transcription_engine": "whisper",
                "translation_model": "claude-3.5-sonnet"
            }
        }
        
    except Exception as e:
        return {
            "transcription": transcribe_result,
            "translation_error": str(e),
            "message": "Transcription succeeded but translation failed"
        }

@app.post("/transcribe-and-analyze")
async def transcribe_and_analyze(
    file: UploadFile = File(...),
    model: str = Form(None),
    language: str = Form("pt"),
    analysis_type: str = Form("all")  # summary, sentiment, actions, all
):
    """Transcribe audio and perform comprehensive analysis."""
    
    # First transcribe
    transcribe_result = await transcribe_optimized(
        file=file,
        model=model,
        language=language,
        clean_repetitions=True,
        apply_corrections=True
    )
    
    if "error" in transcribe_result:
        return transcribe_result
    
    analysis_results = {}
    errors = []
    
    text = transcribe_result["text"]
    
    # Summary
    if analysis_type in ["summary", "all"]:
        try:
            analysis_results["summary"] = await openrouter_client.summarize_text(text)
        except Exception as e:
            errors.append(f"Summary failed: {e}")
    
    # Sentiment
    if analysis_type in ["sentiment", "all"]:
        try:
            analysis_results["sentiment"] = await openrouter_client.analyze_sentiment(text)
        except Exception as e:
            errors.append(f"Sentiment analysis failed: {e}")
    
    # Action items
    if analysis_type in ["actions", "all"]:
        try:
            analysis_results["action_items"] = await openrouter_client.extract_action_items(text)
        except Exception as e:
            errors.append(f"Action items extraction failed: {e}")
    
    # Text improvement
    if analysis_type in ["improve", "all"]:
        try:
            analysis_results["improved_text"] = await openrouter_client.improve_transcription(text)
        except Exception as e:
            errors.append(f"Text improvement failed: {e}")
    
    result = {
        "original_transcription": transcribe_result,
        "analysis": analysis_results,
        "processing": {
            "transcription_engine": "whisper",
            "ai_model": "claude-3.5-sonnet",
            "analysis_type": analysis_type
        }
    }
    
    if errors:
        result["errors"] = errors
    
    return result

@app.post("/improve-transcription")
async def improve_transcription_endpoint(
    text: str = Form(...),
    language: str = Form("pt"),
    ai_model: str = Form("qwen3-32b")  # Novo parâmetro para escolher modelo
):
    """Improve existing transcription using AI."""
    
    try:
        improved = await openrouter_client.improve_transcription(text, model=ai_model)
        
        return {
            "original_text": text,
            "improved_text": improved,
            "processing": {
                "ai_model": ai_model,
                "language": language
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Text improvement failed"
        }

@app.get("/ai-models")
async def list_ai_models():
    """Lista modelos de IA disponíveis via OpenRouter."""
    return {
        "available_models": openrouter_client.list_available_models(),
        "default_model": "qwen3-32b",
        "recommended": {
            "speed": "gpt-4o-mini",
            "quality": "claude-3.5-sonnet", 
            "cost_effective": "qwen3-32b",
            "reasoning": "deepseek-r1"
        }
    }

@app.post("/compare-ai-models")
async def compare_ai_models_endpoint(
    text: str = Form(...),
    task: str = Form("improve"),  # improve, summarize, translate
    models: str = Form("qwen3-32b,claude-3.5-sonnet,gpt-4o-mini")
):
    """Compara diferentes modelos IA na mesma tarefa."""
    
    try:
        model_list = [m.strip() for m in models.split(",")]
        comparison = await openrouter_client.compare_models(text, task, model_list)
        
        # Adiciona ranking por velocidade e qualidade
        sorted_by_speed = sorted(
            comparison.items(), 
            key=lambda x: x[1].get('time', 999)
        )
        
        return {
            "task": task,
            "input_text": text,
            "results": comparison,
            "ranking": {
                "fastest": sorted_by_speed[0][0] if sorted_by_speed else None,
                "slowest": sorted_by_speed[-1][0] if sorted_by_speed else None
            },
            "summary": {
                "models_tested": len(model_list),
                "total_time": sum(r.get('time', 0) for r in comparison.values()),
                "average_time": round(sum(r.get('time', 0) for r in comparison.values()) / len(model_list), 2)
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Model comparison failed"
        }

# ============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Starting Whisper Enhanced API on {HOST}:{PORT}")
    logger.info(f"🎯 Default model: {os.getenv('WHISPER_MODEL', 'base')}")
    logger.info(f"🧹 Clean repetitions: {os.getenv('CLEAN_REPETITIONS', 'true')}")
    uvicorn.run(app, host=HOST, port=PORT)