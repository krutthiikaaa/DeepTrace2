import requests
import os
import time

BASE_URL = "http://localhost:8000/api"

# Valid files
IMAGE_PATH = "/Users/krutthiikaaa/.gemini/antigravity-ide/brain/a7c5600e-4b93-4593-b30a-420c4f4efd78/scratch/repo1/images/lady.jpg"
VIDEO_PATH = "/Users/krutthiikaaa/.gemini/antigravity-ide/brain/a7c5600e-4b93-4593-b30a-420c4f4efd78/scratch/repo1/videos/real-1.mp4"
AUDIO_PATH = "human_speech.wav"
DUMMY_AUDIO_PATH = "dummy.wav"

def test_health():
    print("Testing /health...")
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["models_loaded"] == True
    print("Health check PASS")

def test_valid_inference(endpoint, filepath, content_type):
    print(f"Testing {endpoint} with valid file...")
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f, content_type)}
        resp = requests.post(f"{BASE_URL}/detect/{endpoint}", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        assert "prediction" in data
        assert "confidence" in data
        print(f"Valid inference {endpoint} PASS (Prediction: {data['prediction']}, Conf: {data['confidence']})")

def test_invalid_mime_type(endpoint, filepath):
    print(f"Testing {endpoint} with invalid MIME type...")
    with open(filepath, 'rb') as f:
        # Pass a text file disguised as media, or just wrong MIME type
        files = {'file': (os.path.basename(filepath), f, "text/plain")}
        resp = requests.post(f"{BASE_URL}/detect/{endpoint}", files=files)
        assert resp.status_code == 400
        print(f"Invalid MIME type {endpoint} PASS (Returned 400)")

def test_missing_file(endpoint):
    print(f"Testing {endpoint} with missing file...")
    resp = requests.post(f"{BASE_URL}/detect/{endpoint}")
    assert resp.status_code == 422 # Unprocessable Entity (FastAPI default for missing required param)
    print(f"Missing file {endpoint} PASS (Returned 422)")

def test_empty_corrupted_file(endpoint, content_type):
    print(f"Testing {endpoint} with corrupted file...")
    # Create empty file
    with open("empty.tmp", "wb") as f:
        pass
    with open("empty.tmp", "rb") as f:
        files = {'file': ("empty.tmp", f, content_type)}
        resp = requests.post(f"{BASE_URL}/detect/{endpoint}", files=files)
        assert resp.status_code == 400 # Our custom validation should catch empty files
        print(f"Corrupted file {endpoint} PASS (Returned 400)")
    os.remove("empty.tmp")

def check_cleanup():
    print("Checking cleanup of uploads/ directory...")
    files = os.listdir("uploads")
    # Only .gitkeep should be there
    remaining = [f for f in files if f != ".gitkeep"]
    assert len(remaining) == 0, f"Uploads directory is not empty: {remaining}"
    print("Cleanup PASS")

def main():
    print("Starting API regression tests...\n")
    try:
        test_health()
        
        # Image
        test_valid_inference("image", IMAGE_PATH, "image/jpeg")
        test_invalid_mime_type("image", IMAGE_PATH)
        test_missing_file("image")
        test_empty_corrupted_file("image", "image/jpeg")

        # Video
        test_valid_inference("video", VIDEO_PATH, "video/mp4")
        test_invalid_mime_type("video", VIDEO_PATH)
        test_missing_file("video")
        test_empty_corrupted_file("video", "video/mp4")

        # Audio
        test_valid_inference("audio", AUDIO_PATH, "audio/wav")
        test_valid_inference("audio", DUMMY_AUDIO_PATH, "audio/wav")
        test_invalid_mime_type("audio", AUDIO_PATH)
        test_missing_file("audio")
        test_empty_corrupted_file("audio", "audio/wav")
        
        check_cleanup()
        print("\nALL TESTS PASSED SUCCESSFULLY!")
        
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        exit(1)

if __name__ == "__main__":
    main()
