import os
import shutil
import uuid
# pyrefly: ignore [missing-import]
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

MAX_FILE_SIZE = 50 * 1024 * 1024 # 50 MB

def save_upload_file_tmp(upload_file: UploadFile) -> str:
    """Saves an uploaded file to a temporary location and returns the path. 
    Enforces a strict 50MB size limit to prevent memory/storage exhaustion."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(upload_file.filename)[1]
    if not ext:
        ext = ".tmp"
    
    tmp_filename = f"{uuid.uuid4().hex}{ext}"
    tmp_path = os.path.join(UPLOAD_DIR, tmp_filename)
    
    file_size = 0
    with open(tmp_path, "wb") as buffer:
        while chunk := upload_file.file.read(1024 * 1024):  # Read in 1MB chunks
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                buffer.close()
                cleanup_file(tmp_path)
                raise ValueError(f"File exceeds maximum allowed size of 50MB.")
            buffer.write(chunk)
            
    if file_size == 0:
        cleanup_file(tmp_path)
        raise ValueError("Uploaded file is empty.")
        
    return tmp_path

def cleanup_file(filepath: str):
    """Deletes a file if it exists."""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning up file {filepath}: {e}")
