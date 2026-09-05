import logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.image_detector import detect_image
from backend.services.forensics import perform_ela
from backend.utils.file_handlers import save_upload_file_tmp, cleanup_file
import time

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/image")
async def process_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
    logger.info(f"Received image inference request: {file.filename} ({file.content_type})")
    start_time = time.time()
    tmp_path = None
    try:
        tmp_path = save_upload_file_tmp(file)
        logger.info(f"Starting image inference for {file.filename}...")
        result = detect_image(tmp_path)
        result["success"] = True
        
        logger.info(f"Starting ELA forensics for {file.filename}...")
        ela_result = perform_ela(tmp_path)
        result["forensics"] = {
            "ela": ela_result
        }
        
        duration = round(time.time() - start_time, 2)
        logger.info(f"Image inference completed in {duration}s. Prediction: {result['prediction']}")
        
        return result
    except ValueError as ve:
        logger.error(f"Validation error during image processing: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Internal error during image processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        if tmp_path:
            cleanup_file(tmp_path)
