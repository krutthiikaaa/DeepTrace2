import React, { useEffect, useRef, useState } from 'react';
import { Camera, Loader2, AlertCircle } from 'lucide-react';

interface WebcamCaptureProps {
  onCapture: (file: File) => void;
  onCancel: () => void;
}

const VIDEO_CONSTRAINTS: MediaStreamConstraints = {
  video: {
    facingMode: 'user',
    width: { ideal: 1280 },
    height: { ideal: 720 },
  },
  audio: false,
};

function getCameraErrorMessage(err: unknown): string {
  if (err instanceof DOMException) {
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      return 'Camera access was denied. Please allow camera permission, or upload a photo instead.';
    }
    if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      return 'No camera device was found. Please upload a photo instead.';
    }
    if (err.name === 'NotReadableError') {
      return 'The camera is already in use by another application. Please upload a photo instead.';
    }
  }
  return 'Unable to access the camera. Please upload a photo instead.';
}

const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture, onCancel }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);

  useEffect(() => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError('Your browser does not support camera access. Please upload a photo instead.');
      return;
    }
    let cancelled = false;
    navigator.mediaDevices.getUserMedia(VIDEO_CONSTRAINTS)
      .then((mediaStream) => {
        if (cancelled) {
          mediaStream.getTracks().forEach((t) => t.stop());
          return;
        }
        setStream(mediaStream);
      })
      .catch((err: unknown) => {
        if (!cancelled) setCameraError(getCameraErrorMessage(err));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!stream) return;
    if (videoRef.current) videoRef.current.srcObject = stream;
    return () => {
      stream.getTracks().forEach((t) => t.stop());
    };
  }, [stream]);

  const handleCapture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.videoWidth === 0) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    // Mirroring is CSS-only on the preview; the captured frame stays true-orientation.
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        onCapture(new File([blob], `webcam-capture-${Date.now()}.jpg`, { type: 'image/jpeg' }));
      },
      'image/jpeg',
      0.92,
    );
  };

  if (cameraError) {
    return (
      <div className="upload-container analyzing">
        <AlertCircle size={40} className="webcam-error-icon" />
        <p className="subtitle">{cameraError}</p>
        <button type="button" className="secondary-button" onClick={onCancel}>
          Upload a Photo Instead
        </button>
      </div>
    );
  }

  if (!stream) {
    return (
      <div className="upload-container analyzing">
        <Loader2 className="spinner" size={40} />
        <p className="subtitle">Requesting camera access...</p>
      </div>
    );
  }

  return (
    <>
      <div className="webcam-video-wrapper">
        <video ref={videoRef} autoPlay playsInline muted className="webcam-video" />
      </div>
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <button type="button" className="primary-button webcam-capture-btn" onClick={handleCapture}>
        <Camera size={18} />
        Capture Photo
      </button>
    </>
  );
};

export default WebcamCapture;
