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

app = FastAPI(
    title="Whisper API",
    description="API para transcrição de áudio usando OpenAI Whisper",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available models
class ModelSize(str, Enum):
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"

# Cache for loaded models
models_cache = {}

def get_model(model_size: str):
    """Load and cache Whisper model."""
    if model_size not in models_cache:
        logger.info(f"Loading model: {model_size}")
        models_cache[model_size] = whisper.load_model(model_size)
    return models_cache[model_size]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Whisper API",
        "version": "1.0.0",
        "endpoints": {
            "transcribe": "/transcribe",
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
    """List available Whisper models."""
    return {
        "models": [model.value for model in ModelSize],
        "loaded_models": list(models_cache.keys())
    }


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    model: ModelSize = Form(ModelSize.base, description="Whisper model size"),
    language: Optional[str] = Form(None, description="Language code (e.g., 'en', 'pt')"),
    task: str = Form("transcribe", description="Task: 'transcribe' or 'translate'"),
    temperature: float = Form(0.0, description="Temperature for sampling"),
    verbose: bool = Form(False, description="Enable verbose output")
):
    """
    Transcribe audio file using Whisper.
    
    - **file**: Audio file (mp3, wav, m4a, etc.)
    - **model**: Model size (tiny, base, small, medium, large)
    - **language**: Optional language code for better accuracy
    - **task**: 'transcribe' (same language) or 'translate' (to English)
    - **temperature**: Sampling temperature (0.0 = deterministic)
    - **verbose**: Enable detailed logging
    """
    temp_file = None
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        logger.info(f"Processing file: {file.filename} with model: {model.value}")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Load model
        whisper_model = get_model(model.value)
        
        # Prepare transcription options
        options = {
            "task": task,
            "temperature": temperature,
            "verbose": verbose
        }
        
        if language:
            options["language"] = language
        
        # Transcribe audio
        logger.info(f"Starting transcription with options: {options}")
        result = whisper_model.transcribe(temp_file_path, **options)
        
        # Prepare response
        response = {
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
    file: UploadFile = File(..., description="Audio file to transcribe")
):
    """
    Simple transcription endpoint with default settings (base model, auto-detect language).
    
    - **file**: Audio file (mp3, wav, m4a, etc.)
    """
    return await transcribe_audio(
        file=file,
        model=ModelSize.base,
        language=None,
        task="transcribe",
        temperature=0.0,
        verbose=False
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
