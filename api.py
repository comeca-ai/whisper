"""
FastAPI endpoint for Whisper speech recognition.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
from typing import Optional
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import FunASR
try:
    from funasr import AutoModel
    FUNASR_AVAILABLE = True
    logger.info("FunASR is available")
except ImportError:
    FUNASR_AVAILABLE = False
    logger.warning("FunASR not available. Install with: pip install funasr")

# Try to import Faster Whisper
try:
    from faster_whisper import WhisperModel as FasterWhisperModel
    FASTER_WHISPER_AVAILABLE = True
    logger.info("Faster Whisper is available")
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning("Faster Whisper not available. Install with: pip install faster-whisper")

# Try to import Transformers (Wav2Vec2)
try:
    from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
    import torch
    import torchaudio
    TRANSFORMERS_AVAILABLE = True
    logger.info("Transformers (Wav2Vec2) is available")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Install with: pip install transformers torch torchaudio")

app = FastAPI(
    title="Multi-Model Speech Recognition API",
    description="API para transcrição de áudio usando Whisper, FunASR e outros modelos",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available engines
class Engine(str, Enum):
    whisper = "whisper"
    faster_whisper = "faster-whisper"
    funasr = "funasr"
    wav2vec2 = "wav2vec2"

# Available Whisper models
class WhisperModel(str, Enum):
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"
    turbo = "turbo"

# Available FunASR models
class FunASRModel(str, Enum):
    paraformer_zh = "paraformer-zh"
    paraformer_en = "paraformer-en"
    paraformer_large = "paraformer-large-v2"

# Cache for loaded models
whisper_cache = {}
faster_whisper_cache = {}
funasr_cache = {}
wav2vec2_cache = {}

def get_whisper_model(model_size: str):
    """Load and cache Whisper model."""
    if model_size not in whisper_cache:
        logger.info(f"Loading Whisper model: {model_size}")
        whisper_cache[model_size] = whisper.load_model(model_size)
    return whisper_cache[model_size]

def get_funasr_model(model_name: str):
    """Load and cache FunASR model."""
    if not FUNASR_AVAILABLE:
        raise HTTPException(status_code=503, detail="FunASR not installed")
    
    if model_name not in funasr_cache:
        logger.info(f"Loading FunASR model: {model_name}")
        funasr_cache[model_name] = AutoModel(model=model_name)
    return funasr_cache[model_name]

def get_faster_whisper_model(model_size: str):
    """Load and cache Faster Whisper model."""
    if not FASTER_WHISPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Faster Whisper not installed")
    
    if model_size not in faster_whisper_cache:
        logger.info(f"Loading Faster Whisper model: {model_size}")
        # Use CPU with 4 threads for better performance
        faster_whisper_cache[model_size] = FasterWhisperModel(
            model_size, 
            device="cpu",
            compute_type="int8",  # Quantized for lower memory
            cpu_threads=2
        )
    return faster_whisper_cache[model_size]

def get_wav2vec2_model(model_name: str = "facebook/wav2vec2-base-960h"):
    """Load and cache Wav2Vec2 model."""
    if not TRANSFORMERS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Transformers not installed")
    
    if model_name not in wav2vec2_cache:
        logger.info(f"Loading Wav2Vec2 model: {model_name}")
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name)
        wav2vec2_cache[model_name] = {"processor": processor, "model": model}
    return wav2vec2_cache[model_name]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Multi-Model Speech Recognition API",
        "version": "2.0.0",
        "endpoints": {
            "transcribe": "/transcribe",
            "transcribe-simple": "/transcribe-simple",
            "models": "/models",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/models")
async def list_models():
    """List available models for all engines."""
    return {
        "engines": [engine.value for engine in Engine],
        "whisper_models": [model.value for model in WhisperModel],
        "funasr_models": [model.value for model in FunASRModel] if FUNASR_AVAILABLE else [],
        "loaded_whisper": list(whisper_cache.keys()),
        "loaded_faster_whisper": list(faster_whisper_cache.keys()),
        "loaded_funasr": list(funasr_cache.keys()),
        "loaded_wav2vec2": list(wav2vec2_cache.keys()),
        "engines_available": {
            "whisper": True,
            "faster-whisper": FASTER_WHISPER_AVAILABLE,
            "funasr": FUNASR_AVAILABLE,
            "wav2vec2": TRANSFORMERS_AVAILABLE
        }
    }


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    engine: Engine = Form(Engine.whisper, description="Transcription engine"),
    model: Optional[str] = Form(None, description="Model name (whisper: tiny/base/small/medium/large/turbo, funasr: paraformer-zh/paraformer-en/paraformer-large-v2)"),
    language: Optional[str] = Form(None, description="Language code (e.g., 'en', 'pt', 'zh')"),
    task: str = Form("transcribe", description="Task: 'transcribe' or 'translate' (Whisper only)"),
    temperature: float = Form(0.0, description="Temperature for sampling (Whisper only)"),
    verbose: bool = Form(False, description="Enable verbose output")
):
    """
    Transcribe audio file using multiple engines.
    
    - **file**: Audio file (mp3, wav, m4a, etc.)
    - **engine**: 'whisper' or 'funasr'
    - **model**: Model name (defaults: whisper=base, funasr=paraformer-zh)
    - **language**: Optional language code for better accuracy
    - **task**: 'transcribe' (same language) or 'translate' (to English) - Whisper only
    - **temperature**: Sampling temperature (0.0 = deterministic) - Whisper only
    - **verbose**: Enable detailed logging
    """
    temp_file = None
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Set default model based on engine
        if model is None:
            model = "base" if engine == Engine.whisper else "paraformer-zh"
        
        logger.info(f"Processing file: {file.filename} with engine: {engine.value}, model: {model}")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process based on engine
        if engine == Engine.whisper:
            # Load Whisper model
            whisper_model = get_whisper_model(model)
            
            # Prepare transcription options
            options = {
                "task": task,
                "temperature": temperature,
                "verbose": verbose
            }
            
            if language:
                options["language"] = language
            
            # Transcribe audio
            logger.info(f"Starting Whisper transcription with options: {options}")
            result = whisper_model.transcribe(temp_file_path, **options)
            
            # Prepare response
            response = {
                "engine": "whisper",
                "model": model,
                "text": result["text"],
                "language": result.get("language"),
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
        
        elif engine == Engine.faster_whisper:
            # Load Faster Whisper model
            faster_model = get_faster_whisper_model(model)
            
            # Transcribe audio
            logger.info(f"Starting Faster Whisper transcription")
            segments_iter, info = faster_model.transcribe(
                temp_file_path,
                language=language,
                task=task,
                temperature=temperature,
                vad_filter=True  # Voice Activity Detection for better results
            )
            
            # Convert segments to list
            segments = []
            full_text = []
            for i, segment in enumerate(segments_iter):
                segments.append({
                    "id": i,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })
                full_text.append(segment.text)
            
            # Prepare response
            response = {
                "engine": "faster-whisper",
                "model": model,
                "text": " ".join(full_text),
                "language": info.language if hasattr(info, 'language') else language,
                "segments": segments,
                "performance": {
                    "duration": info.duration if hasattr(info, 'duration') else None,
                    "language_probability": info.language_probability if hasattr(info, 'language_probability') else None
                }
            }
        
        elif engine == Engine.wav2vec2:
            # Load Wav2Vec2 model
            wav2vec2 = get_wav2vec2_model()
            processor = wav2vec2["processor"]
            model_wav2vec = wav2vec2["model"]
            
            # Load audio
            logger.info(f"Starting Wav2Vec2 transcription")
            import librosa
            speech, rate = librosa.load(temp_file_path, sr=16000)
            
            # Process audio
            inputs = processor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
            
            with torch.no_grad():
                logits = model_wav2vec(**inputs).logits
            
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.batch_decode(predicted_ids)[0]
            
            # Prepare response
            response = {
                "engine": "wav2vec2",
                "model": "facebook/wav2vec2-base-960h",
                "text": transcription,
                "language": language or "en",
                "segments": []
            }
        
        elif engine == Engine.funasr:
            # Load FunASR model
            funasr_model = get_funasr_model(model)
            
            # Transcribe audio
            logger.info(f"Starting FunASR transcription")
            result = funasr_model.generate(input=temp_file_path)
            
            # Parse FunASR result
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get("text", "")
                segments = []
                
                # Try to extract timestamps if available
                if "timestamp" in result[0]:
                    timestamps = result[0]["timestamp"]
                    if timestamps:
                        for i, (start, end) in enumerate(timestamps):
                            segments.append({
                                "id": i,
                                "start": start / 1000.0,  # Convert ms to seconds
                                "end": end / 1000.0,
                                "text": text  # FunASR may not split by segments
                            })
            else:
                text = str(result)
                segments = []
            
            # Prepare response
            response = {
                "engine": "funasr",
                "model": model,
                "text": text,
                "language": language or "auto-detected",
                "segments": segments
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown engine: {engine}")
        
        logger.info("Transcription completed successfully")
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")


@app.post("/transcribe-simple")
async def transcribe_simple(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    engine: Engine = Form(Engine.whisper, description="Transcription engine")
):
    """
    Simple transcription endpoint with default settings.
    
    - **file**: Audio file (mp3, wav, m4a, etc.)
    - **engine**: 'whisper' (default) or 'funasr'
    """
    return await transcribe_audio(
        file=file,
        engine=engine,
        model=None,  # Will use defaults
        language=None,
        task="transcribe",
        temperature=0.0,
        verbose=False
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
