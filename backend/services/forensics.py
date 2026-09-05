import cv2
import numpy as np
import base64
import logging

logger = logging.getLogger(__name__)

def perform_ela(filepath: str, quality: int = 90) -> dict:
    """
    Performs Error Level Analysis (ELA) on an image to detect potential manipulation.
    """
    try:
        # 1. Safely decode the image
        img = cv2.imread(filepath, cv2.IMREAD_COLOR)
        
        # Handle corrupted or unreadable images
        if img is None:
            return {
                "available": False,
                "error": "Image could not be read or decoded for ELA."
            }
            
        height, width = img.shape[:2]
        
        # Handle very small or invalid dimensions
        if height < 16 or width < 16:
            return {
                "available": False,
                "error": "Image is too small for reliable ELA."
            }

        # 2. Perform JPEG recompression at a known quality level
        # Compress into memory buffer
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, encoded_img = cv2.imencode('.jpg', img, encode_param)
        
        if not success:
            return {
                "available": False,
                "error": "Failed to recompress image for ELA."
            }
            
        # Decode back to image
        recompressed_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
        
        # 3. Compare original with recompressed
        diff = cv2.absdiff(img, recompressed_img)
        
        # Calculate statistics BEFORE aggressive enhancement
        # Convert to grayscale to evaluate overall magnitude
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        max_diff = float(np.max(diff_gray))
        mean_diff = float(np.mean(diff_gray))
        std_diff = float(np.std(diff_gray))
        
        # Calculate anomaly ratio: ratio of pixels with difference > 20
        anomaly_pixels = np.sum(diff_gray > 20)
        total_pixels = diff_gray.size
        anomaly_ratio = float(anomaly_pixels) / total_pixels
        
        # 4. Generate ELA visualization (Enhance differences)
        # Multiply by a factor to make differences visible. 
        # If max_diff is 0, avoid division by zero.
        if max_diff > 0:
            scale = 255.0 / max_diff
            enhanced_diff = cv2.convertScaleAbs(diff, alpha=scale)
        else:
            enhanced_diff = diff
            
        # Encode visualization to base64
        success, vis_encoded = cv2.imencode('.jpg', enhanced_diff, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if success:
            vis_base64 = base64.b64encode(vis_encoded).decode('utf-8')
            vis_data_uri = f"data:image/jpeg;base64,{vis_base64}"
        else:
            vis_data_uri = None
            
        return {
            "available": True,
            "mean": round(mean_diff, 2),
            "max": round(max_diff, 2),
            "std": round(std_diff, 2),
            "anomaly_ratio": round(anomaly_ratio, 4),
            "image": vis_data_uri
        }

    except Exception as e:
        logger.error(f"Error during ELA analysis: {e}")
        return {
            "available": False,
            "error": "ELA analysis failed or image unsupported"
        }
