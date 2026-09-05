import cv2
import numpy as np
import base64
import logging

logger = logging.getLogger(__name__)

def perform_fft_analysis(filepath: str) -> dict:
    """
    Performs FFT/Frequency-Domain Analysis on an image to detect unusual frequency characteristics.
    Calculates statistics over the magnitude spectrum and returns a visualization.
    """
    try:
        # 1. Decode the uploaded image safely
        img = cv2.imread(filepath, cv2.IMREAD_COLOR)
        
        if img is None:
            return {
                "available": False,
                "error": "Image could not be read or decoded for FFT analysis."
            }
            
        height, width = img.shape[:2]
        
        if height < 16 or width < 16:
            return {
                "available": False,
                "error": "Image is too small for reliable FFT analysis."
            }
            
        # 2. Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. Apply a Hanning window to reduce edge artifacts before FFT
        # (Optional but recommended for cleaner spectra)
        hann_y = np.hanning(height)
        hann_x = np.hanning(width)
        window = np.outer(hann_y, hann_x)
        windowed_img = img_gray * window

        # 4 & 5. Compute the 2D FFT and shift the zero-frequency component to the center
        f = np.fft.fft2(windowed_img)
        fshift = np.fft.fftshift(f)
        
        # 6. Calculate the magnitude spectrum
        # Adding a small constant to prevent log(0)
        magnitude_spectrum = np.log(np.abs(fshift) + 1)
        
        # 7. Calculate Statistics
        # Identify center
        cy, cx = height // 2, width // 2
        
        # Create a mask for the low frequency region (e.g., radius of 1/8th of min dimension)
        radius = min(height, width) // 8
        y, x = np.ogrid[:height, :width]
        mask_area = (x - cx)**2 + (y - cy)**2 <= radius**2
        
        low_freq_region = magnitude_spectrum[mask_area]
        high_freq_region = magnitude_spectrum[~mask_area]
        
        # Raw measurements
        spectral_mean = float(np.mean(magnitude_spectrum))
        spectral_std = float(np.std(magnitude_spectrum))
        spectral_energy = float(np.sum(np.abs(fshift)**2) / (height * width))
        
        # Ratios (based on mean magnitude in the respective regions)
        low_frequency_ratio = float(np.mean(low_freq_region) / spectral_mean) if spectral_mean > 0 else 0.0
        high_frequency_ratio = float(np.mean(high_freq_region) / spectral_mean) if spectral_mean > 0 else 0.0

        # 8. Normalize the visualization for display
        # Scale magnitude spectrum to 0-255 for visualization
        normalized_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
        vis_image = np.uint8(normalized_spectrum)
        
        # Encode visualization to base64
        success, vis_encoded = cv2.imencode('.jpg', vis_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if success:
            vis_base64 = base64.b64encode(vis_encoded).decode('utf-8')
            vis_data_uri = f"data:image/jpeg;base64,{vis_base64}"
        else:
            vis_data_uri = None
            
        return {
            "available": True,
            "spectral_mean": round(spectral_mean, 4),
            "spectral_std": round(spectral_std, 4),
            "high_frequency_ratio": round(high_frequency_ratio, 4),
            "low_frequency_ratio": round(low_frequency_ratio, 4),
            "spectral_energy": round(spectral_energy, 2),
            "image": vis_data_uri
        }

    except Exception as e:
        logger.error(f"Error during FFT analysis: {e}")
        return {
            "available": False,
            "error": "FFT analysis failed or image unsupported"
        }
