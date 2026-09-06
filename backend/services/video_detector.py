import cv2
import torch
import numpy as np
from backend.app import ml_models
from backend.services.image_detector import preprocess_img, crop_largest_face

def preprocess_video(input_video, n_frames=3):
    v_cap = cv2.VideoCapture(input_video)
    if not v_cap.isOpened():
        raise ValueError("Could not open video file.")
        
    try:
        v_len = int(v_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if v_len <= 0:
            raise ValueError("Video file has no valid frames.")

        actual_frames = min(n_frames, v_len) if n_frames else v_len
        if n_frames is None:
            sample = np.arange(0, v_len)
        else:
            sample = np.linspace(0, v_len - 1, actual_frames).astype(int)

        frames = []
        faces_found = 0
        for j in range(v_len):
            success = v_cap.grab()
            if j in sample:
                success, frame = v_cap.retrieve()
                if not success:
                    continue
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame, face_found = crop_largest_face(frame)
                faces_found += int(face_found)
                frame = preprocess_img(frame)
                frames.append(frame)

        if not frames:
            raise ValueError("Could not extract any valid frames from the video.")

        return frames, faces_found
    finally:
        v_cap.release()

def detect_video(filepath: str) -> dict:
    """
    Detects if a video is fake or real using the loaded image model on extracted frames.
    """
    video_frames, faces_found = preprocess_video(filepath, n_frames=3)
    
    img_model = ml_models.img_model
    if img_model is None:
        raise RuntimeError("Image model is not loaded.")
        
    real_faces_list = []
    fake_faces_list = []

    with torch.no_grad():
        for face in video_frames:
            img_grads = img_model.forward(face)
            img_grads = img_grads.cpu().detach().numpy()
            img_grads_np = np.squeeze(img_grads)
            real_faces_list.append(img_grads_np[0])
            fake_faces_list.append(img_grads_np[1])

    real_faces_mean = float(np.mean(real_faces_list))
    fake_faces_mean = float(np.mean(fake_faces_list))

    if real_faces_mean > 0.5:
        confidence = real_faces_mean
        prediction = "REAL"
    else:
        confidence = fake_faces_mean
        prediction = "FAKE"

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "media_type": "video",
        "frames_analyzed": len(video_frames),
        "faces_found_in_frames": faces_found,
        "real_score_mean": round(real_faces_mean, 4),
        "fake_score_mean": round(fake_faces_mean, 4)
    }
