import logging
import os
from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
import torch
# pyrefly: ignore [missing-import]
import onnx
# pyrefly: ignore [missing-import]
from onnx2pytorch import ConvertModel

from backend.models_arch import image as image_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model references
class MLModels:
    img_model = None
    spec_model = None

ml_models = MLModels()

# Define dummy args class for RawNet instantiation
class DummyArgs:
    device = 'cpu'
    in_channels = 1
    gru_node = 1024
    nb_gru_layer = 3
    nb_fc_node = 1024
    nb_classes = 2
    pretrained_image_encoder = False
    freeze_image_encoder = False
    pretrained_audio_encoder = False
    freeze_audio_encoder = False

def load_models():
    checkpoint_dir = "models/checkpoints"
    onnx_path = os.path.join(checkpoint_dir, "efficientnet.onnx")
    ckpt_path = os.path.join(checkpoint_dir, "model.pth")

    if not (os.path.isfile(onnx_path) and os.path.isfile(ckpt_path)):
        logger.warning(
            "Model checkpoints not found in %s (need efficientnet.onnx and model.pth). "
            "Starting API without loaded models; detection endpoints will fail until checkpoints are added.",
            checkpoint_dir,
        )
        return

    logger.info("Loading EfficientNet ONNX Model...")
    onnx_model = onnx.load(onnx_path)
    pytorch_model = ConvertModel(onnx_model)

    logger.info("Loading checkoints from model.pth...")
    ckpt = torch.load(ckpt_path, map_location=torch.device('cpu'))

    # Load Image Model
    rgb_encoder = pytorch_model
    rgb_encoder.load_state_dict(ckpt['rgb_encoder'], strict=True)
    rgb_encoder.eval()
    ml_models.img_model = rgb_encoder
    logger.info("Image model loaded successfully.")

    # Load Audio Model (RawNet)
    args = DummyArgs()
    spec_encoder = image_models.RawNet(args)
    spec_encoder.load_state_dict(ckpt['spec_encoder'], strict=True)
    spec_encoder.eval()
    ml_models.spec_model = spec_encoder
    logger.info("Audio model loaded successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    load_models()
    yield
    # Shutdown
    ml_models.img_model = None
    ml_models.spec_model = None

app = FastAPI(title="DeepTrace2 Media Detection API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.routes import image, video, audio, health

app.include_router(health.router, prefix="/api")
app.include_router(image.router, prefix="/api/detect", tags=["Image Detection"])
app.include_router(video.router, prefix="/api/detect", tags=["Video Detection"])
app.include_router(audio.router, prefix="/api/detect", tags=["Audio Detection"])

@app.get("/")
def read_root():
    return {"message": "Welcome to DeepTrace2 API"}
