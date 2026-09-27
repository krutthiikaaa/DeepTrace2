import cv2
import numpy as np
import logging
from PIL import Image
import os

logger = logging.getLogger(__name__)

def perform_capture_integrity_analysis(filepath: str) -> dict:
    """
    Analyzes an image for capture integrity (e.g., moire patterns, resampling artifacts, glare, missing metadata).
    Returns a structured response without making final authenticity claims.
    """
    indicators = []
    status = "UNCERTAIN"
    explanation = ""

    try:
        if not os.path.isfile(filepath):
            return {"status": "UNAVAILABLE", "indicators": [], "explanation": "Image unavailable."}

        img = cv2.imread(filepath)
        if img is None:
            return {"status": "UNAVAILABLE", "indicators": [], "explanation": "Image unavailable."}

        height, width = img.shape[:2]
        if height < 64 or width < 64:
            return {"status": "UNAVAILABLE", "indicators": ["Resolution too low"], "explanation": "Image is too small for capture integrity analysis."}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Image Quality / Capture Gate (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 50:
            indicators.append("Low image sharpness or heavy compression")

        # 2. Moire / Screen Pattern (FFT analysis)
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = np.log(np.abs(fshift) + 1)
        
        cy, cx = height // 2, width // 2
        y, x = np.ogrid[:height, :width]
        mask_area = (x - cx)**2 + (y - cy)**2 <= (min(height, width) // 4)**2
        high_freq = magnitude_spectrum.copy()
        high_freq[mask_area] = 0
        
        peak_threshold = np.mean(high_freq) + 3 * np.std(high_freq)
        peaks = (high_freq > peak_threshold).sum()
        
        if peaks > (height * width) * 0.005:
            indicators.append("Possible display/screen pattern (Moiré) or repeated high-frequency structure")

        # 3. Screen Boundary Analysis (Canny + Hough lines)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=min(height, width)*0.5, maxLineGap=20)
        
        if lines is not None and len(lines) >= 2:
            indicators.append("Possible rectangular boundaries (Screen border)")

        # 4. Resampling / Display-Recapture Analysis
        if laplacian_var > 3000:
            indicators.append("Possible resampling or unnatural interpolation patterns")

        # 5. Glare / Reflection Analysis
        _, thresholded = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        glare_found = False
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > (height * width) * 0.01: 
                glare_found = True
        if glare_found:
            indicators.append("Possible display glare/reflection")

        # 6. Metadata / EXIF
        has_metadata = False
        try:
            with Image.open(filepath) as pil_img:
                exif = pil_img.getexif()
                if exif:
                    has_metadata = True
        except Exception:
            pass

        if not has_metadata:
            indicators.append("Metadata unavailable")
        else:
            indicators.append("Metadata available")
        
        # Determine Status
        recapture_indicators = ["Possible display/screen pattern (Moiré) or repeated high-frequency structure", 
                                "Possible rectangular boundaries (Screen border)", 
                                "Possible resampling or unnatural interpolation patterns",
                                "Possible display glare/reflection"]
                                
        detected_recaptures = [ind for ind in indicators if ind in recapture_indicators]
        
        if len(detected_recaptures) > 0:
            status = "POSSIBLE_RECAPTURE"
            explanation = "The uploaded image may have been re-presented or captured from another display. This does not prove that the underlying content is manipulated, but direct authenticity assessment may be unreliable."
        elif "Low image sharpness or heavy compression" in indicators:
            status = "UNCERTAIN"
            explanation = "Capture integrity is uncertain due to low image quality."
        else:
            status = "DIRECT_CAPTURE"
            explanation = "Image appears to be a direct capture with no clear signs of screen reproduction."
            
        return {
            "status": status,
            "indicators": indicators,
            "explanation": explanation
        }
        
    except Exception as e:
        logger.error(f"Error in capture integrity analysis: {e}")
        return {
            "status": "UNAVAILABLE",
            "indicators": [],
            "explanation": "Analysis failed."
        }
