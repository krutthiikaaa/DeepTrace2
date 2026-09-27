import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def analyze_temporal_frames(frame_paths: list) -> dict:
    if not frame_paths or len(frame_paths) < 3:
        return {"detected": False, "indicators": []}
        
    try:
        frames = []
        for p in frame_paths:
            img = cv2.imread(p)
            if img is not None:
                # Resize to small size for fast processing and noise reduction
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (128, 128))
                frames.append(resized)
                
        if len(frames) < 3:
            return {"detected": False, "indicators": []}

        video_vol = np.stack(frames, axis=0).astype(np.float32)
        indicators = []
        
        # 1. Global Intensity Flicker (Frame-to-frame mean variations)
        frame_means = np.mean(video_vol, axis=(1, 2))
        diffs = np.diff(frame_means)
        
        # If the differences oscillate back and forth (typical of PWM dimming / refresh rates interacting with camera shutter)
        sign_changes = np.sum(np.diff(np.sign(diffs)) != 0)
        
        if len(diffs) >= 4 and sign_changes >= len(diffs) * 0.4:
            if np.std(diffs) > 0.5:
                indicators.append("Temporal display pattern")
                
        # 2. Rolling Band Analysis (Row-wise temporal differences)
        # Displays often have rolling shutter artifacts where horizontal bands move vertically
        row_means = np.mean(video_vol, axis=2) # shape: (num_frames, 128)
        row_diffs = np.diff(row_means, axis=0) # shape: (num_frames-1, 128)
        
        # Check if row differences have high variance (moving bands)
        band_variance = np.var(row_diffs, axis=1) # Variance across rows for each frame diff
        if np.mean(band_variance) > 5.0: # Arbitrary threshold for significant rolling bands
            indicators.append("Rolling band / temporal pattern")

        # 3. High Local Temporal Variance (Display Refresh vs Static Object)
        temporal_var = np.var(video_vol, axis=0)
        temporal_mean = np.mean(video_vol, axis=0)
        cv = np.sqrt(temporal_var) / (temporal_mean + 1e-5)
        
        high_var_pixels = np.sum(cv > 0.05)
        total_pixels = cv.shape[0] * cv.shape[1]
        
        if high_var_pixels > total_pixels * 0.15:
            indicators.append("Consistent temporal variation across display region")

        return {
            "detected": len(indicators) > 0,
            "indicators": indicators,
            "frames_analyzed": len(frames)
        }

    except Exception as e:
        logger.error(f"Error in temporal capture analysis: {e}")
        return {"detected": False, "indicators": []}
