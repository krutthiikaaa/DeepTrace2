# DeepTrace2 Deployment Guide

This guide details how to deploy DeepTrace2's decoupled architecture: a Vercel-hosted React frontend and a Render-hosted FastAPI backend.

## 1. Prerequisites

- **GitHub Repository**: The codebase must be pushed to a GitHub repository.
- **Git LFS**: You **MUST** ensure Git Large File Storage (LFS) is correctly configured and that `models/checkpoints/model.pth` and `models/checkpoints/efficientnet.onnx` are uploaded as real binary files, not LFS text pointers.
- **Vercel Account**: For the frontend.
- **Render Account**: For the backend.

## 2. Backend Deployment (Render)

Render requires authentication via GitHub. **You must perform this step manually.**

### Setup
1. Log into [Render](https://dashboard.render.com).
2. Create a new **Web Service**.
3. Connect your GitHub repository.
4. Render will automatically detect the `render.yaml` configuration in the root directory.
5. If you prefer manual setup, use these settings:
   - **Root Directory**: `.` (leave blank)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt` (Note: `opencv-python-headless` is required and has been configured to prevent libgl1 OS dependency errors).
   - **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: `3.9.6` (enforced via `.python-version`).

### Resource Requirements (CRITICAL)
- The backend loads over ~135 MB of models directly into RAM, alongside PyTorch, ONNX, and OpenCV runtimes.
- **DO NOT** use the absolute lowest free tier if it crashes with OOM (Out Of Memory) errors during model load. You may need a tier with at least 512MB to 1GB of RAM.

### Environment Variables
Once deployed, set the following environment variable in your Render dashboard:
- `ALLOWED_ORIGINS`: Your upcoming Vercel frontend URL (e.g., `https://deeptrace-frontend.vercel.app`).

### Verify Deployment
Once deployed, visit `https://<your-render-url>/api/health`. 
You should receive:
```json
{
  "status": "ok",
  "models_loaded": true
}
```

## 3. Frontend Deployment (Vercel)

Vercel requires authentication via GitHub. **You must perform this step manually.**

### Setup
1. Log into [Vercel](https://vercel.com).
2. Create a **New Project** and import your GitHub repository.
3. **Important**: Set the **Root Directory** to `frontend/`.
4. Vercel will automatically detect Vite. The settings should be:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Environment Variables
Before deploying, add the following environment variable to Vercel:
- `VITE_API_URL`: Your Render backend URL (e.g., `https://deeptrace-backend.onrender.com/api`).
*(Do not add a trailing slash).*

### HTTPS & Camera Access
Vercel automatically provisions HTTPS for your domain. This is strictly required for `navigator.mediaDevices.getUserMedia()` to function. The Live Camera component will automatically utilize the secure context to request camera permissions.

## 4. Local Development Reference

To run the application locally without deployment:

**Backend:**
```bash
cd /Users/krutthiikaaa/Desktop/projects/DeepTrace2
source .venv/bin/activate
python -m uvicorn backend.app:app --reload
```

**Frontend:**
```bash
cd /Users/krutthiikaaa/Desktop/projects/DeepTrace2/frontend
npm run dev
```

## 5. Troubleshooting
- **API Request Fails / CORS Error**: Ensure the Render backend has the `ALLOWED_ORIGINS` environment variable set exactly to the Vercel URL without a trailing slash.
- **Model Load Fails on Render**: If Render logs show memory exhaustion, you must upgrade the instance type. If Render logs show `DecodeError: Error parsing message with type 'onnx.ModelProto'`, your Git LFS objects did not download correctly to Render. Ensure Render's Git LFS support is enabled in your account settings.
- **Camera Not Working**: Ensure you are accessing the Vercel site via `https://`. Browsers explicitly block camera access over insecure `http://` connections.
