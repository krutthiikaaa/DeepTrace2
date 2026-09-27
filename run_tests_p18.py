import cv2
import numpy as np
import os
from backend.services.capture_integrity_analysis import perform_capture_integrity_analysis
from backend.services.evidence_fusion import perform_evidence_fusion

def create_synthetic_images():
    os.makedirs("test_images", exist_ok=True)
    
    # --- TEST A: Direct Real Camera Image ---
    # Good quality, no patterns, no borders, no temporal flicker
    img_a = np.ones((480, 640, 3), dtype=np.uint8) * 128
    cv2.putText(img_a, "Direct Real Document", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # Add noise to give it some gradient variance and variance in laplacian
    noise = np.random.normal(0, 10, img_a.shape).astype(np.uint8)
    img_a = cv2.add(img_a, noise)
    cv2.imwrite("test_images/test_a.jpg", img_a)
    for i in range(5):
        cv2.imwrite(f"test_images/test_a_{i}.jpg", img_a.copy()) # No temporal change
        
    # --- TEST B: Phone with Border Visible ---
    # Has a rectangular boundary, spatial pattern (moire), temporal flicker, and resampling (high microgradient)
    img_b = np.zeros((480, 640, 3), dtype=np.uint8)
    # Phone border
    cv2.rectangle(img_b, (100, 50), (540, 430), (50, 50, 50), -1) # Phone body
    cv2.rectangle(img_b, (110, 60), (530, 420), (200, 200, 200), -1) # Screen
    # Spatial moire pattern on screen
    for y in range(60, 420, 2):
        cv2.line(img_b, (110, y), (530, y), (255, 255, 255), 1)
    for x in range(110, 530, 2):
        cv2.line(img_b, (x, 60), (x, 420), (255, 255, 255), 1)
    
    cv2.imwrite("test_images/test_b.jpg", img_b)
    # Temporal flicker frames
    for i in range(5):
        frame = img_b.copy()
        if i % 2 == 0:
            frame[60:420, 110:530] = np.clip(frame[60:420, 110:530] * 0.8, 0, 255) # Dimmer
        cv2.imwrite(f"test_images/test_b_{i}.jpg", frame)
        
    # --- TEST C: Phone with Border HIDDEN ---
    # Screen fills the entire frame. No borders visible.
    # Has spatial pattern, resampling (high local gradient variance but structured), and temporal flicker
    img_c = np.zeros((480, 640, 3), dtype=np.uint8)
    # Intense checkerboard for high gradient and moire
    for y in range(0, 480, 2):
        cv2.line(img_c, (0, y), (640, y), (200, 200, 200), 1)
    for x in range(0, 640, 2):
        cv2.line(img_c, (x, 0), (x, 480), (200, 200, 200), 1)
    
    cv2.imwrite("test_images/test_c.jpg", img_c)
    # Temporal flicker frames
    for i in range(5):
        frame = img_c.copy()
        if i % 2 == 0:
            frame = np.clip(frame * 0.8, 0, 255).astype(np.uint8) # Global flicker
        cv2.imwrite(f"test_images/test_c_{i}.jpg", frame)

    # --- TEST E: Natural Repeating Pattern ---
    # Striped shirt (spatial periodicity) but NO temporal flicker, NO resampling
    img_e = np.ones((480, 640, 3), dtype=np.uint8) * 180
    for x in range(0, 640, 40): # Wide, soft stripes
        cv2.rectangle(img_e, (x, 0), (x+20, 480), (160, 160, 160), -1)
    img_e = cv2.GaussianBlur(img_e, (15, 15), 0) # Soft gradients, not pixelated
    
    cv2.imwrite("test_images/test_e.jpg", img_e)
    for i in range(5):
        cv2.imwrite(f"test_images/test_e_{i}.jpg", img_e.copy()) # No temporal flicker

def print_result(name, result):
    print(f"\n{'='*50}\n{name}\n{'='*50}")
    print(f"Status: {result['status']}")
    print("Indicators:")
    for key, val in result["indicators"].items():
        print(f"  {key}: {val['status']}")
    print(f"Explanation: {result['explanation']}")

def run_tests():
    create_synthetic_images()
    
    # Test A
    res_a = perform_capture_integrity_analysis("test_images/test_a.jpg", [f"test_images/test_a_{i}.jpg" for i in range(5)])
    print_result("TEST A - DIRECT CAPTURE", res_a)
    
    # Fusion for Test A (mock real prediction)
    fusion_a = perform_evidence_fusion("REAL", 0.95, {}, res_a)
    print(f"FUSION RISK: {fusion_a['risk_level']} (Expected: LOW_RISK or REVIEW_REQUIRED)")

    # Test B
    res_b = perform_capture_integrity_analysis("test_images/test_b.jpg", [f"test_images/test_b_{i}.jpg" for i in range(5)])
    print_result("TEST B - PHONE BORDER VISIBLE", res_b)

    fusion_b = perform_evidence_fusion("REAL", 0.95, {}, res_b)
    print(f"FUSION RISK: {fusion_b['risk_level']} (Expected: REVIEW_REQUIRED due to POSSIBLE_RECAPTURE)")

    # Test C
    res_c = perform_capture_integrity_analysis("test_images/test_c.jpg", [f"test_images/test_c_{i}.jpg" for i in range(5)])
    print_result("TEST C - PHONE BORDER HIDDEN", res_c)

    fusion_c = perform_evidence_fusion("REAL", 0.95, {}, res_c)
    print(f"FUSION RISK: {fusion_c['risk_level']} (Expected: REVIEW_REQUIRED due to POSSIBLE_RECAPTURE)")

    # Test E
    res_e = perform_capture_integrity_analysis("test_images/test_e.jpg", [f"test_images/test_e_{i}.jpg" for i in range(5)])
    print_result("TEST E - NATURAL REPEATING PATTERN", res_e)
    
    fusion_e = perform_evidence_fusion("REAL", 0.95, {}, res_e)
    print(f"FUSION RISK: {fusion_e['risk_level']}")

if __name__ == "__main__":
    run_tests()
