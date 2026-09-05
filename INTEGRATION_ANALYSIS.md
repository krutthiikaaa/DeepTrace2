# Integration Analysis: AI-Generated Video Detector & Security Under Diffusion

This document provides a comprehensive technical analysis of two repositories, evaluating their architectures, dependencies, and requirements for integration into a new, unified deepfake and AI-generated media detection application.

## 1. Repository 1 Analysis (AI-Generated-Video-Detector)
**Source**: https://github.com/Pranesh-2005/AI-Generated-Video-Detector
- **Programming language**: Python (3.10 recommended).
- **Frameworks/libraries**: PyTorch, TensorFlow, OpenCV (`cv2`), Gradio, ONNX (`onnx`, `onnx2pytorch`), MoviePy.
- **Entry points**: `app.py` (Gradio Interface), `inference.py`, `inference_2.py` (backend inference scripts).
- **Main application flow**: The user uploads media via Gradio. The media is passed to `inference_2.py`. For videos, frames are extracted evenly. Images/frames are preprocessed (resized to 256x256, normalized) and passed through the model. The predictions are averaged (for video) and a threshold (0.5) is used to classify Fake vs. Real, yielding a confidence score.
- **Model architecture**: Uses EfficientNetV2 for visual data (via ONNX conversion) and RawNet for audio. There is also a multimodal model (`ETMC`).
- **Model checkpoint/weights requirements**: Requires pre-trained weights (`checkpoints/efficientnet.onnx` or `checkpoints/model.pth`), which are not tracked in the repo and must be downloaded.
- **Preprocessing pipeline**: 
  - Image: BGR image divided by 255, resized to (256, 256), converted to tensor.
  - Video: OpenCV extracts `n_frames` (default 3 or 5) evenly spaced frames, converts BGR to RGB, then applies the image preprocessing.
- **Inference pipeline**: `img_model.forward(face)` outputs a tensor. It uses an argmax or probability threshold (> 0.5) to decide if media is REAL or FAKE.
- **Input formats**: Image formats (JPG/PNG), Video formats (MP4), Audio (FLAC/WAV).
- **Output formats**: Text prediction ("The [media] is REAL/FAKE. Confidence score is: X%").
- **Hardware/CPU/GPU requirements**: The inference script maps the model to the CPU by default (`map_location=torch.device('cpu')`), but PyTorch natively supports GPU if modified.
- **Dependency requirements**: See `requirements.txt` (`torch`, `opencv-python`, `onnx`, `onnx2pytorch`, etc.).
- **Files actually required for inference**: `inference_2.py`, `models/image.py`, `models/TMC.py`.
- **Files that are only for training/experiments**: `save_ckpts.py`, `main.py` (likely training based on args), `datasets/`.
- **Dataset requirements**: Not required for inference (training uses FakeAVCeleb, etc.).
- **License**: MIT License.
- **Attribution requirements**: MIT requires preserving the copyright notice.
- **Restrictions on redistribution**: None, as long as the MIT license is included.

## 2. Repository 2 Analysis (Security-Under-Diffusion)
**Source**: https://github.com/jeevanparajuli856/Security-Under-Diffusion
- **Programming language**: Python.
- **Frameworks/libraries**: PyTorch (>=2.0), Torchvision, Pillow (PIL), scikit-learn, numpy, pandas, tqdm.
- **Entry points**: `runners/run_dire.py`, `runners/run_hfreq.py`.
- **Main application flow**: Evaluates datasets using CSV manifests. Loads an image, applies preprocessing, runs through the chosen detector (DIRE or HFreq), saves the probability scores to a CSV, and computes evaluation metrics (AUC, FPR).
- **Model architecture**: 
  - **DIRE**: Pretrained diffusion reconstruction error (uses ResNet50).
  - **HFreq**: Frequency-domain CNN (Custom CNN with 4 blocks and adaptive average pooling).
- **Model checkpoint/weights requirements**: Checkpoints located in `detectors/checkpoints/` (e.g., `imagenet_adm.pth`), which are needed for inference.
- **Preprocessing pipeline**:
  - **DIRE**: Uses PIL, resizes to 256, center crops to 224, converts to tensor (values 0-1), and normalizes with specific mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.
- **Inference pipeline**: The image tensor is unsqueezed (`[1, 3, 224, 224]`) and passed to `model(xb).sigmoid().item()` to get the probability of being synthetic (fake).
- **Input formats**: PNG and JPEG images.
- **Output formats**: Float probability representing the likelihood of being synthetic.
- **Hardware/CPU/GPU requirements**: Supports GPU but has a `--use_cpu` fallback flag.
- **Dependency requirements**: `torch>=2.0`, `torchvision>=0.15`, `Pillow>=9.4`, `scikit-learn`.
- **Files actually required for inference**: `detectors/dire/dire_wrapper.py`, `detectors/dire/load_model.py`, `detectors/hfreq/model.py`, `preprocessing/dire.py`, `preprocessing/hfreq.py`.
- **Files that are only for training/experiments**: `runners/run_all.py`, `evaluation/`, dataset splits and manifests.
- **Dataset requirements**: Required only for evaluation scripts (CSV manifests), not for raw inference.
- **License**: No explicit LICENSE file found in the root directory. 
- **Attribution requirements**: Must cite the paper "Security Under Diffusion Benchmark" by Jeevan Parajuli.
- **Restrictions on redistribution**: Ambiguous due to missing license file, but citation is explicitly requested for usage.

## 3. Image Detection Pipeline
The unified image detection pipeline will accept an image (via path or array) and run it through two separate branches:
- **Branch A (Repo 1)**: Converts image to BGR (if using OpenCV), resizes to 256x256, scales by 1/255, and runs through EfficientNetV2 to detect deepfake face manipulations.
- **Branch B (Repo 2)**: Converts image to RGB (via PIL), resizes to 256, crops to 224, applies ImageNet normalization, and runs through DIRE (ResNet50) and HFreq to detect diffusion-generated artifacts.
The output will be an aggregated result displaying probabilities from both distinct detectors.

## 4. Video Detection Pipeline
- Uses OpenCV (from Repo 1) to extract `N` evenly spaced frames from a video file.
- Iterates over the frames and passes them to **both** Image Detection pipelines (Branch A and Branch B).
- Averages the confidence scores across all frames for both the EfficientNet model and the Diffusion models to provide a final video-level classification.

## 5. Dependency Comparison & Conflicts
- **PyTorch**: Repo 1 uses an unspecified `torch` version while Repo 2 requires `torch>=2.0`. They should easily coexist on `torch>=2.0`.
- **Image Processing**: Repo 1 uses OpenCV (`cv2`) while Repo 2 uses Pillow (`PIL`). This is not a conflict; both libraries can be installed. We simply need to handle the BGR/RGB conversion correctly when passing frames from OpenCV to Repo 2's PIL-based preprocessing.
- **Other Dependencies**: `onnx` and `onnx2pytorch` are unique to Repo 1. `scikit-learn` and `pandas` are unique to Repo 2 (mostly for evaluation, potentially unneeded for bare inference). There are no direct dependency conflicts.

## 6. Model/Checkpoint Requirements
To run both pipelines successfully, the unified app will need:
- `efficientnet.onnx` or `model.pth` (from Repo 1, must be downloaded/provided).
- `imagenet_adm.pth` and corresponding HFreq weights (from Repo 2, must be migrated from `detectors/checkpoints/`).

## 7. License and Attribution Analysis
- **Repo 1**: MIT License. Must include the MIT license text and Pranesh's copyright notice in the project.
- **Repo 2**: No formal license. The README explicitly requests citation of Jeevan Parajuli's paper. We must add a clear attribution section to the new project's documentation acknowledging both authors.

## 8. Compatibility Issues
- **Image Data Types**: OpenCV loads images as Numpy arrays (BGR), whereas `torchvision.transforms` (Repo 2) expects PIL Images (RGB) for its `Resize` and `CenterCrop` operations. We must convert `cv2` frames to `PIL.Image` objects before passing them to Repo 2's `preprocess_dire`.
- **Device Placement**: Repo 1 explicitly hardcodes `map_location=torch.device('cpu')`. We will need to parameterize this to enable seamless GPU support across both models.

## 9. Minimum Files/Functions Required
**From Repo 1:**
- `models/image.py`, `models/TMC.py` (Architecture definitions)
- The model loading logic and `preprocess_img` from `inference_2.py`.
- OpenCV video frame extraction logic.

**From Repo 2:**
- `detectors/dire/dire_wrapper.py`, `detectors/dire/load_model.py`
- `detectors/hfreq/model.py`
- `preprocessing/dire.py`, `preprocessing/hfreq.py`

## 10. Recommended Architecture for the New Project
```
DeepTrace2/
├── app.py                # Main unified frontend/API (e.g. Gradio/FastAPI)
├── core/
│   ├── video_utils.py    # Frame extraction (OpenCV)
│   └── aggregation.py    # Logic to combine scores
├── detectors/
│   ├── deepfake/         # Repo 1 (EfficientNet)
│   │   ├── models/
│   │   ├── preprocess.py
│   │   └── wrapper.py
│   └── diffusion/        # Repo 2 (DIRE/HFreq)
│       ├── models/
│       ├── preprocess.py
│       └── wrapper.py
├── checkpoints/          # All downloaded weights
└── requirements.txt
```

## 11. Step-by-Step Integration Plan
1. **Scaffold Directory Structure**: Create the new project architecture (`core`, `detectors/deepfake`, `detectors/diffusion`, `checkpoints`).
2. **Port Repo 1**: Copy `models` and adapt inference logic into a clean class-based wrapper in `detectors/deepfake/wrapper.py`. Remove hardcoded CPU map locations.
3. **Port Repo 2**: Copy `detectors` and `preprocessing` for DIRE/HFreq into `detectors/diffusion/wrapper.py`.
4. **Build Core Logic**: Write a master inference pipeline (`core/video_utils.py`) that handles taking an image/video, extracting frames, formatting them for PIL (for Repo 2) and OpenCV (for Repo 1), and feeding them to both wrappers.
5. **Score Aggregation**: Write logic to average frames and combine detector confidence scores.
6. **Frontend**: Build a unified Gradio or FastAPI interface (`app.py`).

## 12. Risks/Blockers
- **Missing Weights**: The weights for Repo 1 are not in the repository and must be acquired by the user (as stated in their README). If we do not have these weights, Repo 1 inference cannot run.
- **Performance**: Running EfficientNet, DIRE (ResNet50), and HFreq sequentially per frame on a video will be computationally heavy on a CPU.

## 13. Hackathon MVP Recommendation
For a hackathon MVP:
- Limit video frame extraction to a maximum of 3-5 frames to keep inference times manageable.
- Focus purely on **EfficientNet (Repo 1)** for Face deepfakes and **DIRE (Repo 2)** for diffusion deepfakes. Skip HFreq and Audio models initially to save complexity.
- Wrap everything in a simple Streamlit or Gradio UI that clearly displays "Face Manipulation Score" and "Diffusion Generation Score" side by side.

---

### Conclusion
**Yes, both repositories can realistically and successfully be integrated into one unified Python application.** 
Since both rely on PyTorch, they share a common ecosystem. The only integration challenge is ensuring image tensors are formatted correctly for each respective model (OpenCV/Numpy for Repo 1, PIL/Torchvision for Repo 2), which is easily solvable by mapping color spaces and data structures during the pipeline's preprocessing phase.
