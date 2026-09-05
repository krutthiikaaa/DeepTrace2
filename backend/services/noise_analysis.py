import cv2
import numpy as np
import base64
import logging

logger = logging.getLogger(__name__)

def perform_noise_analysis(filepath: str) -> dict:
    """
    Performs Noise/Residual Analysis on an image to detect unusual pixel-level noise/residual patterns.
    It uses a lightweight Gaussian blur to create a smoothed version and calculates the residual magnitude.
    """
    try:
        # 1. Decode the uploaded image
        img = cv2.imread(filepath, cv2.IMREAD_COLOR)
        
        # Handle corrupted or unreadable images
        if img is None:
            return {
                "available": False,
                "error": "Image could not be read or decoded for noise analysis."
            }
            
        height, width = img.shape[:2]
        
        # Handle very small or invalid dimensions
        if height < 16 or width < 16:
            return {
                "available": False,
                "error": "Image is too small for reliable noise analysis."
            }

        # 2. Convert to grayscale or appropriate luminance representation
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. Create a denoised/smoothed version using Gaussian blur
        # A 5x5 kernel provides a gentle smoothing
        smoothed = cv2.GaussianBlur(img_gray, (5, 5), 0)
        
        # 4. Calculate the residual: original image - smoothed image
        # Use absolute residual magnitude
        # Convert to float32 to prevent underflow during subtraction
        residual = cv2.absdiff(img_gray.astype(np.float32), smoothed.astype(np.float32))
        
        # 5. Use the absolute residual magnitude for statistical analysis
        max_res = float(np.max(residual))
        mean_res = float(np.mean(residual))
        std_res = float(np.std(residual))
        
        # Calculate anomaly ratio: ratio of pixels with residual magnitude > 10 (configurable threshold)
        threshold = 10.0
        anomaly_pixels = np.sum(residual > threshold)
        total_pixels = residual.size
        anomaly_ratio = float(anomaly_pixels) / total_pixels
        
        # 6. Normalize the residual representation for visualization
        # Multiply by a factor to make differences visible. 
        if max_res > 0:
            scale = 255.0 / max_res
            enhanced_residual = cv2.convertScaleAbs(residual, alpha=scale)
        else:
            enhanced_residual = np.zeros_like(img_gray, dtype=np.uint8)
            
        # Encode visualization to base64
        success, vis_encoded = cv2.imencode('.jpg', enhanced_residual, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if success:
            vis_base64 = base64.b64encode(vis_encoded).decode('utf-8')
            vis_data_uri = f"data:image/jpeg;base64,{vis_base64}"
        else:
            vis_data_uri = None
            
        return {
            "available": True,
            "mean": round(mean_res, 2),
            "max": round(max_res, 2),
            "std": round(std_res, 2),
            "anomaly_ratio": round(anomaly_ratio, 4),
            "image": vis_data_uri
        }

    except Exception as e:
        logger.error(f"Error during noise analysis: {e}")
        return {
            "available": False,
            "error": "Noise analysis failed or image unsupported"
        }
