import requests
import time
import os
import numpy as np
import scipy.io.wavfile as wavfile

BASE_URL = "http://localhost:8000/api/detect"

# Paths to the sample files in scratch directory
IMAGE_PATH = "/Users/krutthiikaaa/.gemini/antigravity-ide/brain/a7c5600e-4b93-4593-b30a-420c4f4efd78/scratch/repo1/images/lady.jpg"
VIDEO_PATH = "/Users/krutthiikaaa/.gemini/antigravity-ide/brain/a7c5600e-4b93-4593-b30a-420c4f4efd78/scratch/repo1/videos/real-1.mp4"
AUDIO_PATH = "dummy.wav"

def generate_dummy_wav(path):
    # generate 1 second of random noise at 16000 hz
    samplerate = 16000
    data = np.random.uniform(-1, 1, samplerate).astype(np.float32)
    wavfile.write(path, samplerate, data)
    return path

def test_endpoint(url, filepath, content_type):
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f, content_type)}
        print(f"Testing {url} with {os.path.basename(filepath)}...")
        try:
            resp = requests.post(url, files=files)
            if resp.status_code == 200:
                print("SUCCESS:", resp.json())
                return resp.json()
            else:
                print("FAILED:", resp.status_code, resp.text)
                return None
        except Exception as e:
            print("ERROR:", e)
            return None

def main():
    audio_wav = generate_dummy_wav(AUDIO_PATH)
    
    print("\n--- Testing Image ---")
    img_res = test_endpoint(f"{BASE_URL}/image", IMAGE_PATH, "image/jpeg")
    
    print("\n--- Testing Video ---")
    vid_res = test_endpoint(f"{BASE_URL}/video", VIDEO_PATH, "video/mp4")
    
    print("\n--- Testing Audio ---")
    aud_res = test_endpoint(f"{BASE_URL}/audio", audio_wav, "audio/wav")

    print("\n\n==== FINAL RESULTS REPORT ====")
    print("Endpoint\tInput\tPrediction\tConfidence\tStatus")
    
    def status(res): return "PASS" if res else "FAIL"
    def pred(res): return res.get("prediction", "N/A") if res else "N/A"
    def conf(res): return res.get("confidence", "N/A") if res else "N/A"
    
    print(f"Image\t{os.path.basename(IMAGE_PATH)}\t{pred(img_res)}\t{conf(img_res)}\t{status(img_res)}")
    print(f"Video\t{os.path.basename(VIDEO_PATH)}\t{pred(vid_res)}\t{conf(vid_res)}\t{status(vid_res)}")
    print(f"Audio\t{os.path.basename(audio_wav)}\t{pred(aud_res)}\t{conf(aud_res)}\t{status(aud_res)}")

if __name__ == "__main__":
    main()
