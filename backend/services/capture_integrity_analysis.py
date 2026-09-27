import cv2
import numpy as np
import logging
from PIL import Image
import os
from backend.services.temporal_capture_analysis import analyze_temporal_frames

logger = logging.getLogger(__name__)

def detect_spatial_periodicity(gray: np.ndarray) -> bool:
    """Detects spatial periodicity (moire) by analyzing patches instead of the global image."""
    height, width = gray.shape
    patch_size = min(height, width) // 4
    if patch_size < 32:
        return False
        
    patches = [
        gray[0:patch_size, 0:patch_size],
        gray[0:patch_size, -patch_size:],
        gray[-patch_size:, 0:patch_size],
        gray[-patch_size:, -patch_size:],
        gray[height//2 - patch_size//2 : height//2 + patch_size//2, width//2 - patch_size//2 : width//2 + patch_size//2]
    ]
    
    anomalous_patches = 0
    for patch in patches:
        f = np.fft.fft2(patch)
        fshift = np.fft.fftshift(f)
        magnitude = np.log(np.abs(fshift) + 1)
        
        # Mask low frequencies
        cy, cx = patch_size // 2, patch_size // 2
        y, x = np.ogrid[:patch_size, :patch_size]
        mask_area = (x - cx)**2 + (y - cy)**2 <= (patch_size // 4)**2
        magnitude[mask_area] = 0
        
        # Look for distinct, strong symmetric peaks
        peak_threshold = np.mean(magnitude) + 4 * np.std(magnitude)
        peaks = (magnitude > peak_threshold).sum()
        
        if peaks > (patch_size * patch_size) * 0.005:
            anomalous_patches += 1
            
    # Require multiple regions to show periodicity (rules out localized natural patterns like a striped shirt in the corner)
    return anomalous_patches >= 2

def detect_resampling_artifacts(gray: np.ndarray) -> bool:
    """Detects interpolation/resampling artifacts locally."""
    # Look for unnatural gradients / ringing (e.g. high frequency grid artifacts from displays)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    lap_var = laplacian.var()
    
    # Simple global variance is not enough. Let's check local gradient consistency.
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(sobelx**2 + sobely**2)
    
    # Displays often have very consistent micro-gradients due to pixel sub-structure.
    # We look for a high mean gradient magnitude but low variance in patches
    if np.mean(grad_mag) > 40 and np.var(grad_mag) < 1500 and lap_var > 1500:
        return True
    return False

def perform_capture_integrity_analysis(filepath: str, temporal_paths: list = None) -> dict:
    """
    Analyzes an image for capture integrity (e.g., moire patterns, resampling artifacts, glare, missing metadata).
    Returns a structured dictionary of categorical indicators.
    """
    indicators = {
        "screen_boundary": {"status": "UNAVAILABLE", "note": "No physical display boundary visible"},
        "spatial_periodicity": {"status": "NO_CLEAR_ANOMALY"},
        "temporal_display": {"status": "NO_CLEAR_ANOMALY"},
        "resampling": {"status": "NO_CLEAR_ANOMALY"},
        "glare_reflection": {"status": "NO_CLEAR_ANOMALY"},
        "metadata": {"status": "UNAVAILABLE"},
        "quality": {"status": "PASS"}
    }
    status = "UNCERTAIN"
    explanation = ""
    temporal_data = {}

    try:
        if not os.path.isfile(filepath):
            return {"status": "UNAVAILABLE", "indicators": indicators, "explanation": "Image unavailable."}

        img = cv2.imread(filepath)
        if img is None:
            return {"status": "UNAVAILABLE", "indicators": indicators, "explanation": "Image unavailable."}

        height, width = img.shape[:2]
        if height < 64 or width < 64:
            indicators["quality"] = {"status": "FAIL", "note": "Resolution too low"}
            return {"status": "UNAVAILABLE", "indicators": indicators, "explanation": "Image is too small for analysis."}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Quality Check
        if cv2.Laplacian(gray, cv2.CV_64F).var() < 50:
            indicators["quality"] = {"status": "FAIL", "note": "Low sharpness or heavy compression"}

        # 2. Spatial Periodicity (Moiré)
        if detect_spatial_periodicity(gray):
            indicators["spatial_periodicity"] = {"status": "POSSIBLE_ANOMALY", "note": "Periodic spatial structures detected across regions"}

        # 3. Screen Boundary
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=min(height, width)*0.5, maxLineGap=20)
        if lines is not None and len(lines) >= 2:
            indicators["screen_boundary"] = {"status": "POSSIBLE_ANOMALY", "note": "Possible rectangular display boundaries visible"}

        # 4. Resampling / Interpolation
        if detect_resampling_artifacts(gray):
            indicators["resampling"] = {"status": "POSSIBLE_ANOMALY", "note": "Unnatural interpolation or micro-gradient consistency detected"}

        # 5. Glare
        _, thresholded = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        glare_found = False
        for cnt in contours:
            if cv2.contourArea(cnt) > (height * width) * 0.01:
                glare_found = True
        if glare_found:
            indicators["glare_reflection"] = {"status": "POSSIBLE_ANOMALY", "note": "Possible display glare detected"}

        # 6. Metadata
        try:
            with Image.open(filepath) as pil_img:
                if pil_img.getexif():
                    indicators["metadata"] = {"status": "AVAILABLE"}
        except Exception:
            pass
        
        # 7. Temporal Analysis
        if temporal_paths and len(temporal_paths) > 0:
            temporal_result = analyze_temporal_frames(temporal_paths)
            temporal_data["frames_analyzed"] = temporal_result.get("frames_analyzed", 0)
            if temporal_result.get("detected"):
                indicators["temporal_display"] = {"status": "POSSIBLE_ANOMALY", "note": ", ".join(temporal_result.get("indicators", []))}
        
        # Determine Status via Corroboration
        has_temporal = indicators["temporal_display"]["status"] == "POSSIBLE_ANOMALY"
        has_spatial = indicators["spatial_periodicity"]["status"] == "POSSIBLE_ANOMALY"
        has_resampling = indicators["resampling"]["status"] == "POSSIBLE_ANOMALY"
        has_boundary = indicators["screen_boundary"]["status"] == "POSSIBLE_ANOMALY"
        
        # A phone border is NOT required, nor is it sufficient alone.
        # Require multiple independent signals.
        is_recapture = False
        
        if has_temporal and has_spatial:
            is_recapture = True
        elif has_temporal and has_resampling:
            is_recapture = True
        elif has_spatial and has_resampling and (has_boundary or indicators["glare_reflection"]["status"] == "POSSIBLE_ANOMALY"):
            is_recapture = True
        elif has_boundary and has_temporal:
            is_recapture = True
        # NOTE: has_boundary + has_spatial is NO LONGER sufficient without resampling or temporal, to avoid falsely flagging a bordered document with a pattern.
            
        if is_recapture:
            status = "POSSIBLE_RECAPTURE"
            explanation = "Capture-integrity analysis found evidence consistent with a reproduced or previously displayed image. The underlying content may have been re-presented from another display or source."
        elif indicators["quality"]["status"] == "FAIL":
            status = "UNCERTAIN"
            explanation = "Capture integrity is uncertain due to low image quality."
        else:
            status = "DIRECT_CAPTURE"
            explanation = "No reliable evidence of re-presentation detected. The media appears to be a direct capture."
            
        result = {
            "status": status,
            "indicators": indicators,
            "explanation": explanation
        }
        if temporal_data:
            result["temporal_data"] = temporal_data
            
        return result
        
    except Exception as e:
        logger.error(f"Error in capture integrity analysis: {e}")
        return {
            "status": "UNAVAILABLE",
            "indicators": indicators,
            "explanation": "Analysis failed."
        }
