import cv2
import torch
import numpy as np
from backend.app import ml_models

def preprocess_img(face):
    face = face / 255.0
    face = cv2.resize(face, (256, 256))
    face_pt = torch.unsqueeze(torch.Tensor(face), dim=0) 
    return face_pt

def detect_image(filepath: str) -> dict:
    """
    Detects if an image is fake or real using the loaded image model.
    """
    img = cv2.imread(filepath)
    if img is None:
        raise ValueError("Invalid image file or could not be read by OpenCV.")
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    face_pt = preprocess_img(img)
    
    img_model = ml_models.img_model
    if img_model is None:
        raise RuntimeError("Image model is not loaded.")
        
    with torch.no_grad():
        img_grads = img_model.forward(face_pt)
        img_grads = img_grads.cpu().detach().numpy()
        img_grads_np = np.squeeze(img_grads)
        
    # The output is typically a 2D array if there are classes, wait, in inference_2 it was:
    # img_grads_np[0] for REAL, img_grads_np[1] for FAKE
    # If img_grads_np[0] > 0.5: REAL
    
    if img_grads_np[0] > 0.5:
        confidence = float(img_grads_np[0])
        prediction = "REAL"
    else:
        confidence = float(img_grads_np[1])
        prediction = "FAKE"
        
    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "media_type": "image"
    }
