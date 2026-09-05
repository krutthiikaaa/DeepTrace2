import logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.audio_detector import detect_audio
from backend.utils.file_handlers import save_upload_file_tmp, cleanup_file
import time

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/audio")
async def process_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
        
    logger.info(f"Received audio inference request: {file.filename} ({file.content_type})")
    start_time = time.time()
    tmp_path = None
    try:
        tmp_path = save_upload_file_tmp(file)
        logger.info(f"Starting audio inference for {file.filename}...")
        result = detect_audio(tmp_path)
        result["success"] = True
        
        duration = round(time.time() - start_time, 2)
        logger.info(f"Audio inference completed in {duration}s. Prediction: {result['prediction']}")
        
        return result
    except ValueError as ve:
        logger.error(f"Validation error during audio processing: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Internal error during audio processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        if tmp_path:
            cleanup_file(tmp_path)
