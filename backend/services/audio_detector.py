# pyrefly: ignore [missing-import]
import torch
import numpy as np
# pyrefly: ignore [missing-import]
import scipy.io.wavfile as wavfile
from backend.app import ml_models

def preprocess_audio(audio_data):
    # The model expects a 1D or 2D array reshaped to (1, samples)
    # We ensure it's float32
    audio_data = audio_data.astype(np.float32)
    
    # If stereo, convert to mono by averaging channels
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
        
    audio_pt = torch.unsqueeze(torch.Tensor(audio_data), dim=0)
    return audio_pt

def detect_audio(filepath: str) -> dict:
    """
    Detects if an audio file is fake or real using the loaded audio model (RawNet).
    """
    try:
        sample_rate, audio_data = wavfile.read(filepath)
    except Exception as e:
        raise ValueError(f"Could not read audio file (must be WAV format). Error: {e}")
        
    if len(audio_data) < 1000:
        raise ValueError("Audio file is too short to extract meaningful features.")
        
    audio = preprocess_audio(audio_data)
    
    spec_model = ml_models.spec_model
    if spec_model is None:
        raise RuntimeError("Audio model is not loaded.")

    with torch.no_grad():
        spec_grads = spec_model.forward(audio)
        spec_grads_inv = np.exp(spec_grads.cpu().detach().numpy().squeeze())

    max_value_idx = np.argmax(spec_grads_inv)

    # In the original repo inference: 
    # if max_value_idx > 0.5: REAL
    # Actually max_value_idx is an index (0 or 1) because it's argmax.
    # So if it's 1 it's REAL, if 0 it's FAKE (or vice versa based on their logic).
    # Their code:
    # max_value = np.argmax(spec_grads_inv)
    # if max_value > 0.5: preds = round(100 - (max_value*100), 3); text2 = "REAL"
    # else: preds = round(max_value*100, 3); text2 = "FAKE"
    # Wait, their confidence logic is weird `100 - max_value*100` where max_value is 0 or 1.
    # If max_value == 1 (REAL): preds = 0.
    # Let's provide the actual probabilities from spec_grads_inv.
    
    prob_fake = float(spec_grads_inv[0])
    prob_real = float(spec_grads_inv[1])
    
    if max_value_idx == 1:
        prediction = "REAL"
        confidence = prob_real
    else:
        prediction = "FAKE"
        confidence = prob_fake

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "media_type": "audio"
    }
