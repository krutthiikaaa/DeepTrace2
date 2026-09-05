# DeepTrace2

DeepTrace2 is a **KYC media authenticity and risk analysis tool**. It combines:

- An **AI deepfake/synthetic-media detector** (EfficientNet-B7 for images/video, RawNet for audio), and
- A set of **classical forensic checks** for images (Error Level Analysis, noise/residual analysis, FFT frequency analysis, face & eye consistency)

...fused into a single, explainable risk report (`LOW_RISK` / `REVIEW_REQUIRED` / `HIGH_RISK`) intended to support manual KYC review, not replace it.

See [INTEGRATION_ANALYSIS.md](INTEGRATION_ANALYSIS.md) and [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for background on how the underlying AI model was sourced and validated.

> **Disclaimer**: This is a prototype. The AI model checkpoints are third-party pretrained weights (see [models/checkpoints/NOTICE.md](models/checkpoints/NOTICE.md)), not trained or scientifically validated by this project. Risk scores are operational heuristics, not calibrated probabilities. Do not use this as the sole basis for a real identity/fraud decision.

---

## Architecture

```
DeepTrace2/
├── backend/                FastAPI service (AI models + forensics)
│   ├── app.py               Entry point: loads models, registers routes
│   ├── models_arch/         Model architecture definitions
│   ├── routes/               API endpoints (image, video, audio, health)
│   ├── services/              Detectors + forensic analyzers + evidence fusion
│   └── utils/                 File upload handling
├── frontend/                React + TypeScript + Vite SPA
├── models/checkpoints/       AI model weights (efficientnet.onnx, model.pth) — via Git LFS
├── requirements.txt          Backend Python dependencies
└── haarcascade_*.xml         OpenCV Haar cascades (bundled with opencv-python, kept here for reference)
```

Flow: the frontend uploads a file → `POST /api/detect/{image,video,audio}` → AI model inference → (images only) ELA + noise + FFT + face/eye forensics → evidence fusion produces a risk level and explanation → frontend renders the report.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.11** | Required specifically. Newer Pythons (3.13/3.14) do not yet have compatible wheels for `torch`/`onnx2pytorch`/some other deps — using them will cause confusing install failures. Check available versions with `py -0` (Windows) or `python3.11 --version` (macOS/Linux). |
| **Node.js 18+** | Tested with Node 24. |
| **Git LFS** | Model checkpoints are stored via Git LFS. Install from [git-lfs.com](https://git-lfs.com/) **before** cloning, or run `git lfs pull` after cloning if the files under `models/checkpoints/` look tiny (a few hundred bytes = LFS pointer, not the real weights). |

---

## Setup

### 1. Clone

```bash
git lfs install          # one-time, per machine
git clone https://github.com/krutthiikaaa/DeepTrace2.git
cd DeepTrace2
```

If you already cloned before installing Git LFS, run `git lfs pull` to fetch the real checkpoint files.

### 2. Backend

Create a virtual environment with **Python 3.11** and install dependencies:

```powershell
# Windows
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
# macOS / Linux
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Run the API from the **repo root** (it's imported as the `backend` package):

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

On startup you should see `Image model loaded successfully.` and `Audio model loaded successfully.`. Verify with:

```bash
curl http://localhost:8000/api/health
# {"status":"ok","models_loaded":true}
```

If `models_loaded` is `false`, see [Troubleshooting](#troubleshooting).

### 3. Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the printed URL (default `http://localhost:5173`). `frontend/.env` already points the UI at `http://localhost:8000/api`; change `VITE_API_URL` there if your backend runs elsewhere.

---

## Using the app

1. Open the frontend in a browser.
2. Pick a tab (Image / Video / Audio) and upload a file.
3. Click Analyze. Images get the full risk report (AI signal + forensic evidence + explanation); video/audio return the raw AI prediction and confidence.

---

## Troubleshooting

- **`models_loaded: false` at `/api/health`** — the checkpoint files are missing or are still LFS pointer stubs. Check `models/checkpoints/efficientnet.onnx` is ~23MB and `models/checkpoints/model.pth` is ~117MB (not a few hundred bytes); if they're tiny, run `git lfs pull`.
- **`pip install` fails on `torch`/`onnx2pytorch`/etc.** — you're likely on a Python version without prebuilt wheels yet. Recreate the venv with Python 3.11.
- **Face & eye analysis returns `"unavailable"` / mentions `CascadeClassifier`** — this happens on `opencv-python` 5.x, which doesn't expose `cv2.CascadeClassifier`. `requirements.txt` pins `opencv-python<5`; if you still hit this, delete your venv and reinstall.
- **Backend fails to import `backend.routes.video`** — make sure you're on a commit that includes the video route fix (a corrupted import line was removed); update to the latest `main`.
- **Git LFS quota errors when cloning** — GitHub's free LFS tier is 1GB storage and 1GB bandwidth/month, shared across everyone cloning this repo. If clones start failing with an LFS bandwidth error, the monthly quota has likely been exhausted; it resets monthly, or a data pack can be purchased on the repo's billing settings.

---

## Tests

- `backend/tests/test_forensics.py` — self-contained pytest unit tests for the ELA module.
- `backend/tests/test_api.py`, `test_endpoints.py`, `test_scenarios.py` — integration/smoke scripts that expect a running backend; some contain machine-specific paths from earlier development and may need small edits (asset paths, `sys.path`) to run in a new environment.

Run the pytest-based tests with:

```bash
pip install pytest requests
pytest backend/tests/test_forensics.py
```

---

## License

No license file is currently specified for this repository. The bundled model checkpoints in `models/checkpoints/` are MIT-licensed third-party weights — see [models/checkpoints/NOTICE.md](models/checkpoints/NOTICE.md) for the full notice.
