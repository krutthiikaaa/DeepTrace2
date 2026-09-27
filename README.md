# DeepTrace — KYC Media Authenticity & Risk Analyzer

> Detect. Investigate. Explain.

DeepTrace is an explainable KYC (Know Your Customer) media verification system that combines AI-based media detection, digital forensic analysis, capture-integrity analysis, and conservative evidence fusion to support human KYC review.

## ⚠️ The Problem
In modern KYC and identity verification, simply classifying an uploaded image as "REAL" or "FAKE" using an AI model is insufficient. Attackers frequently bypass simple verifications through:
- **AI-generated media** (Deepfakes, Stable Diffusion).
- **Manipulated images** (Face swaps, digital alterations).
- **Screen Recapture / Re-presented Media** (Photographing a digital screen displaying a fraudulent ID or face).
- **Recompression/Editing** (Hiding manipulation traces).

When an AI model analyzes a photograph of a phone screen, it may genuinely detect the real camera sensor noise and classify the image as "REAL", bypassing traditional AI deepfake detectors. DeepTrace solves this by treating *content authenticity* and *capture integrity* as separate but equally critical components.

## 💡 The Solution
DeepTrace utilizes a multi-layered, explainable architecture rather than relying on a single "black box" model.

```
KYC Media
    ↓
AI Detection (Deepfake / Synthetic signal)
    ↓
Digital Forensics (ELA, Noise, FFT, Face/Eye)
    ↓
Capture Integrity (Screen/Moiré, Interpolation, Glare)
    ↓
Evidence Fusion (Rule-based corroboration)
    ↓
Explainable KYC Risk Report (LOW_RISK, REVIEW_REQUIRED, HIGH_RISK)
```

## ✨ Key Features
- **AI-Based Media Detection**: Evaluates Image, Video, and Audio media for synthetic generation traces using PyTorch/ONNX models.
- **Error Level Analysis (ELA)**: Detects inconsistent compression levels indicating possible splicing.
- **Noise/Residual Analysis**: Extracts high-frequency camera noise to find inconsistencies.
- **FFT / Frequency Analysis**: Analyzes the frequency domain for unnatural spectral patterns.
- **Face & Eye Analysis**: Checks facial feature consistency, eye alignment, and illumination.
- **Capture Integrity Analysis**: Evaluates the image for signs of being a photograph of a digital screen or printed paper.
  - *Spatial Periodicity (Moiré patterns)*
  - *Resampling/Interpolation artifacts*
  - *Screen Boundary detection*
  - *Display Glare detection*
  - *Image Quality checks*
  - *Temporal Display analysis (if live video)*
- **Live Camera Capture**: The frontend supports live webcam capture for direct KYC verification.
- **Evidence Fusion**: Fuses multiple forensic signals and AI predictions using conservative, transparent heuristics to assign a final risk tier.
- **Explainable Risk Report**: Generates a human-readable report detailing exactly *why* a risk level was assigned.

## 🔍 Forensic Modules
These forensic modules provide *supporting signals*, not standalone proof of manipulation:
- **ELA (Error Level Analysis)**: Re-saves the image at a known quality and compares it to the original. Spliced regions often compress differently.
- **Noise/Residual**: Isolates high-frequency noise using denoising filters. AI-generated images or spliced regions often lack natural camera sensor noise.
- **FFT (Fast Fourier Transform)**: Converts the image to the frequency domain to identify periodic artifacts common in GANs or unnatural sharpening.
- **Face/Eye Consistency**: Detects asymmetric lighting or unnatural eye alignment frequently seen in poor deepfakes.
- **Capture Integrity**: A specialized module to detect re-presented media. Photographing an image displayed on another device creates a *new* real camera photograph. Capture integrity looks for the artifacts of the display medium (pixels, screen edges, moiré).

## ⚖️ Evidence Fusion
DeepTrace avoids arbitrary weighted "authenticity scores." Instead, it relies on conservative rule-based evidence fusion to categorize risk.

It evaluates:
- **AI Evidence**: Strong, Moderate, or Weak signal.
- **Supporting / Conflicting Signals**: Do the forensic modules agree with the AI?
- **Unavailable Signals**: Are certain checks unavailable (e.g., no face detected)?

**Supported Risk Outcomes:**
- `LOW_RISK`: Strong AI "REAL" prediction + clean forensics + clean capture integrity + sufficient evidence.
- `REVIEW_REQUIRED`: Insufficient evidence, mixed signals, or possible capture recapture.
- `HIGH_RISK`: Strong AI "FAKE" prediction + supporting forensic anomalies.

## 📊 Explainability
Every API response generates a dynamic, human-readable report explaining:
- The primary AI result and confidence.
- Which forensic findings were anomalous vs. clean.
- Any capture integrity concerns.
- A summary of supporting/conflicting/unavailable evidence.
- The final reviewer recommendation.

## 🏗️ Architecture

```
  React + TypeScript + Vite (Frontend)
                  ↓
          FastAPI (Backend)
                  ↓
        ┌─────────┼─────────┐
        ↓         ↓         ↓
    AI Model  Forensics  Capture
   (PyTorch) (OpenCV)   Integrity
        └─────────┼─────────┘
                  ↓
           Evidence Fusion
                  ↓
           KYC Risk Report
```

## 🛠️ Technology Stack

| Component | Technologies |
| :--- | :--- |
| **Frontend** | React, TypeScript, Vite |
| **Backend** | Python 3.9, FastAPI, Uvicorn |
| **AI/ML** | PyTorch, ONNX, ONNX2PyTorch, timm |
| **Computer Vision** | OpenCV (`opencv-python-headless`), NumPy, SciPy |
| **Storage** | Git LFS (for model checkpoints) |

## 📁 Project Structure
```text
DeepTrace2/
├── backend/
│   ├── app.py                     # FastAPI application entrypoint
│   ├── routes/                    # API route handlers
│   ├── services/                  # Forensic & AI logic
│   ├── models_arch/               # PyTorch model definitions
│   └── tests/                     # Test suite
├── frontend/
│   ├── src/                       # React source code
│   └── package.json
├── models/
│   └── checkpoints/               # Git LFS tracked AI models (.pth, .onnx)
└── requirements.txt               # Python dependencies
```

## 🚀 Local Setup

### 1. Clone & Pull Models
```bash
git clone https://github.com/krutthiikaaa/DeepTrace2.git
cd DeepTrace2
git lfs install
git lfs pull
```

### 2. Backend Setup
```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app:app --reload
```
*The backend will be available at `http://127.0.0.1:8000`*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*The frontend will be available at `http://localhost:5173`*

## ⚙️ Environment Configuration
To connect the frontend to a specific backend (useful for deployment), create a `frontend/.env` file:
```env
VITE_API_URL=http://127.0.0.1:8000/api
```

## 🔌 API Endpoints
- `GET /api/health`: Returns system status and verifies if models are loaded into memory.
- `POST /api/detect/image`: Accepts an image upload and returns a full JSON risk assessment and forensic report.
- `POST /api/detect/video`: Accepts a video upload, extracts frames, and analyzes them for temporal and spatial anomalies.
- `POST /api/detect/audio`: Accepts an audio file and analyzes it for synthetic voice generation.



## 🧪 Testing
The backend test suite verifies the API routes, evidence fusion, and capture integrity logic.
```bash
pytest backend/tests/
```

## 📸 Demo
*Note: Screenshots will be added to `docs/screenshots/`.*
- [Analysis Dashboard](docs/screenshots/analysis.png)
- [KYC Risk Report](docs/screenshots/risk-report.png)
- [Forensic Visualizations](docs/screenshots/forensics.png)

## 🎯 Use Cases
- **Digital Banking & Fintech Onboarding**: Verifying user-uploaded IDs and selfies.
- **Identity Verification (KYC)**: Supporting human compliance teams with forensic data.
- **Fraud Investigation**: Analyzing suspected tampered documents or deepfakes.
- **Digital Trust & Safety**: Verifying media integrity for high-stakes platforms.

## 🛑 Limitations
- **AI Confidence is NOT Proof**: A high AI confidence score is a statistical prediction, not absolute proof of authenticity or fraud.
- **Forensic False Positives**: Compression artifacts (ELA) or noise anomalies can occur naturally in heavily compressed or poorly lit genuine images.
- **Capture Integrity is Not Perfect**: Detecting a photograph of a screen relies on specific artifacts (Moiré, pixels, glare) which can be obscured by distance, focus, or high-quality screens.
- **Metadata**: EXIF data is easily stripped by social media platforms and messaging apps.
- **Human Review**: DeepTrace is a decision-support tool. Uncertain or conflicting cases **require human review**.

## 🔮 Future Scope
- Stronger presentation-attack detection (PAD).
- Document authenticity analysis and OCR consistency checks.
- Face-to-ID matching and liveness detection.
- Audit trails and PDF report generation for compliance officers.

## ⚖️ Disclaimer
*DeepTrace is a research/prototype decision-support system. Its outputs constitute supporting forensic evidence and risk signals, rather than definitive proof of fraud or authenticity. It is designed to assist, not replace, human compliance review.*

---
*Built as a hackathon project focused on AI-assisted media authenticity and KYC security.*
