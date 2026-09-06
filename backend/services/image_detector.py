import cv2
import torch
import numpy as np
from backend.app import ml_models

FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
FACE_MARGIN_RATIO = 0.3  # extra context around the detected face box


def crop_largest_face(img_rgb: np.ndarray) -> tuple[np.ndarray, bool]:
    """
    Detects the largest face in an RGB image and returns a cropped region
    (with a margin) around it. Falls back to the full image if no face is
    found, since the classifier was trained on face crops, not full scenes.
    """
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) == 0:
        return img_rgb, False

    fx, fy, fw, fh = max(faces, key=lambda rect: rect[2] * rect[3])
    height, width = img_rgb.shape[:2]
    margin_x = int(fw * FACE_MARGIN_RATIO)
    margin_y = int(fh * FACE_MARGIN_RATIO)

    x1 = max(0, fx - margin_x)
    y1 = max(0, fy - margin_y)
    x2 = min(width, fx + fw + margin_x)
    y2 = min(height, fy + fh + margin_y)

    return img_rgb[y1:y2, x1:x2], True


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

    # The classifier was trained on cropped face regions, not full scenes;
    # crop to the largest detected face before feeding it in.
    face_img, face_found = crop_largest_face(img)

    face_pt = preprocess_img(face_img)

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
        "media_type": "image",
        "face_found": face_found
    }
