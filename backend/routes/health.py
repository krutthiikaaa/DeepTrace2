# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from backend.app import ml_models

router = APIRouter()

@router.get("/health")
def health_check():
    models_loaded = ml_models.img_model is not None and ml_models.spec_model is not None
    return {
        "status": "ok",
        "models_loaded": models_loaded
    }
