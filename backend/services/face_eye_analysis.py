import cv2
import numpy as np
import base64
import logging
import os

logger = logging.getLogger(__name__)

def perform_face_eye_analysis(filepath: str) -> dict:
    """
    Performs Face & Eye Consistency Analysis on an image to provide supporting forensic evidence.
    Detects faces and eyes, and computes simple visual consistency measurements.
    """
    try:
        # 1. Decode the uploaded image
        img = cv2.imread(filepath, cv2.IMREAD_COLOR)
        if img is None:
            return {
                "available": False,
                "error": "Image could not be read or decoded for face/eye analysis."
            }
            
        height, width = img.shape[:2]
        if height < 16 or width < 16:
            return {
                "available": False,
                "error": "Image is too small for reliable face/eye analysis."
            }
            
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load OpenCV Haar cascades
        if not hasattr(cv2, 'CascadeClassifier'):
            return {
                "available": False,
                "error": "OpenCV CascadeClassifier not available in this cv2 version."
            }

        face_cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml') if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades') else ''
        eye_cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_eye.xml') if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades') else ''
        
        if not face_cascade_path or not os.path.exists(face_cascade_path) or not os.path.exists(eye_cascade_path):
            return {
                "available": False,
                "error": "OpenCV Haar cascade files not found in environment."
            }
            
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        
        # 2. Detect Faces
        faces = face_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return {
                "available": False,
                "face_detected": False,
                "error": "No reliable face detected"
            }
            
        # Select primary face (largest area)
        primary_face = max(faces, key=lambda rect: rect[2] * rect[3])
        (fx, fy, fw, fh) = primary_face
        
        response = {
            "available": True,
            "face_detected": True,
            "face_count": len(faces),
            "primary_face_selected": True,
            "both_eyes_detected": False,
            "eye_analysis": {
                "available": False
            }
        }
        
        # Draw face bounding box for visualization
        vis_img = img.copy()
        cv2.rectangle(vis_img, (fx, fy), (fx+fw, fy+fh), (255, 0, 0), 2)
        
        # 3. Detect Eyes within the face region
        # Eyes are typically in the upper half of the face
        roi_gray = img_gray[fy:fy+int(fh/1.8), fx:fx+fw]
        roi_color = vis_img[fy:fy+int(fh/1.8), fx:fx+fw]
        
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(15, 15))
        
        # If we have at least 2 eyes detected, pick the two largest
        if len(eyes) >= 2:
            eyes = sorted(eyes, key=lambda rect: rect[2] * rect[3], reverse=True)[:2]
            
            # Sort eyes left-to-right based on x coordinate
            eyes = sorted(eyes, key=lambda rect: rect[0])
            left_eye = eyes[0]
            right_eye = eyes[1]
            
            # Coordinates relative to the face ROI
            (lx, ly, lw, lh) = left_eye
            (rx, ry, rw, rh) = right_eye
            
            # Draw eyes
            cv2.rectangle(roi_color, (lx, ly), (lx+lw, ly+lh), (0, 255, 0), 2)
            cv2.rectangle(roi_color, (rx, ry), (rx+rw, ry+rh), (0, 255, 0), 2)
            
            # Center points
            lcx, lcy = lx + lw/2.0, ly + lh/2.0
            rcx, rcy = rx + rw/2.0, ry + rh/2.0
            cv2.circle(roi_color, (int(lcx), int(lcy)), 2, (0, 0, 255), -1)
            cv2.circle(roi_color, (int(rcx), int(rcy)), 2, (0, 0, 255), -1)
            
            # 4. Compute consistency measurements
            # Vertical alignment difference (normalized by face height)
            vertical_diff = abs(lcy - rcy) / fh
            
            # Eye size difference (normalized by primary eye area)
            left_area = lw * lh
            right_area = rw * rh
            size_diff = abs(left_area - right_area) / max(left_area, right_area)
            
            # Brightness difference
            left_eye_roi = roi_gray[ly:ly+lh, lx:lx+lw]
            right_eye_roi = roi_gray[ry:ry+rh, rx:rx+rw]
            
            left_brightness = np.mean(left_eye_roi)
            right_brightness = np.mean(right_eye_roi)
            brightness_diff = abs(left_brightness - right_brightness) / 255.0
            
            response["both_eyes_detected"] = True
            response["eye_analysis"] = {
                "available": True,
                "eye_center_alignment_difference": round(float(vertical_diff), 4),
                "eye_size_difference": round(float(size_diff), 4),
                "brightness_difference": round(float(brightness_diff), 4)
            }
            
        # Encode visualization
        success, vis_encoded = cv2.imencode('.jpg', vis_img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if success:
            vis_base64 = base64.b64encode(vis_encoded).decode('utf-8')
            response["image"] = f"data:image/jpeg;base64,{vis_base64}"
            
        return response

    except Exception as e:
        logger.error(f"Error during face/eye analysis: {e}")
        return {
            "available": False,
            "error": "Face/eye analysis failed"
        }
