# Validation Report

## 1. Repository 1 Final Validation (AI-Generated-Video-Detector)
### Environment
- **Python version**: 3.9
- **PyTorch version**: 2.8.0
- **TensorFlow version**: Not required/installed! (Tests proved it is unnecessary for inference)
- **ONNX version**: 1.19.1
- **ONNX2PyTorch version**: 0.5.3
- **OpenCV version**: 5.0.0.93
- **NumPy version**: 2.0.2
- **Timm version**: 1.0.29

### Model Checkpoints
- `checkpoints/efficientnet.onnx`: Exists (downloaded via LFS manually), Valid, Not directly loaded (handled by PyTorch translation).
- `checkpoints/model.pth`: Exists (downloaded via LFS manually, 111MB), Valid, successfully loads both `rgb_encoder` and `spec_encoder`.

### Image Detection
- **Status**: Successful.
- **Input**: `images/lady.jpg` (RGB tensor, Shape: `[1, 256, 256, 3]`).
- **Output**: `IMAGE RESULT: The image is FAKE.`
- **Confidence**: `52.16%`
- **Result**: Image loading, preprocessing, and inference worked flawlessly.

### Video Detection
- **Status**: Successful.
- **Input**: `videos/real-1.mp4`
- **Output**: `VIDEO RESULT: The video is REAL.`
- **Confidence**: `60.74%`
- **Result**: OpenCV correctly extracted 3 frames by default, preprocessed them, averaged their predictions, and returned the final confidence.

### Audio Detection
- **Status**: Usable / Ready.
- **Required Model**: RawNet (implemented in `models/image.py`).
- **Checkpoint**: Uses `spec_encoder` from `checkpoints/model.pth`.
- **Pre-processing**: Casts input audio directly to a PyTorch tensor.
- **Output Tested**: `AUDIO RESULT: The audio is FAKE.` (Tested via dummy 64600 sample rate waveform). The model successfully loads and processes the forward pass without crashing.

### CPU Performance
- **Practicality**: Yes, CPU inference is highly practical. The entire script including imports, model loading from disk, OpenCV video frame extraction, and PyTorch inference took approximately 7 seconds on the machine.

### GPU Support
- The code currently hardcodes `map_location=torch.device('cpu')`. It can easily be changed to `cuda` or `mps` for GPU acceleration, but CPU is sufficient for MVP.

### Dependencies
- Minimum inference does **NOT** require `tensorflow`, `librosa`, `moviepy`, or `albumentations`. It runs entirely on `torch`, `opencv-python`, `onnx`, `onnx2pytorch`, and `timm`.

### Problems
- Missing Git LFS checkpoints (resolved manually).
- The face detection (MTCNN) mentioned in their README is actually missing from `inference_2.py`. It just resizes the full image/frame to 256x256. This is fine for deepfakes if the face is large, but might need actual MTCNN added back later.

### Required Fixes
- None for basic inference. It works out-of-the-box with the correct packages.

---

## 2. Repository 2 Final Validation (Security-Under-Diffusion)
- **Status**: Abandoned per user request (Due to Missing License & Missing Checkpoints).

---

## 3. Final Status Table

| Modality | Status | Model | Checkpoint | Inference | CPU Practical |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Image | READY | EfficientNet-b7 | `model.pth` (`rgb_encoder`) | Working | Yes |
| Video | READY | EfficientNet-b7 | `model.pth` (`rgb_encoder`) | Working | Yes |
| Audio | READY | RawNet | `model.pth` (`spec_encoder`) | Working | Yes |

