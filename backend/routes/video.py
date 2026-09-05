
from cv2.utils import logging
from multiprocessing import resource_sharer
import resource
source .venv/bin/activateimport logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.video_detector import detect_video
from backend.utils.file_handlers import save_upload_file_tmp, cleanup_file
import time

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/video")
async def process_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video.")
        
    logger.info(f"Received video inference request: {file.filename} ({file.content_type})")
    start_time = time.time()
    tmp_path = None
    try:
        tmp_path = save_upload_file_tmp(file)
        logger.info(f"Starting video inference for {file.filename}...")
        result = detect_video(tmp_path)
        result["success"] = True
        
        duration = round(time.time() - start_time, 2)
        logger.info(f"Video inference completed in {duration}s. Prediction: {result['prediction']}")
        
        return result
    except ValueError as ve:
        logger.error(f"Validation error during video processing: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Internal error during video processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        if tmp_path:
            cleanup_file(tmp_path)
