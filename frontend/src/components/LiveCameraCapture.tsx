import React, { useRef, useState, useEffect } from 'react';
import { Camera, RefreshCw, Check, AlertCircle } from 'lucide-react';
import { detectImage } from '../services/api';
import type { DetectionResult } from '../types/detection';

interface Props {
  onResult: (result: DetectionResult) => void;
  onError: (msg: string) => void;
}

const LiveCameraCapture: React.FC<Props> = ({ onResult, onError }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [capturedBlob, setCapturedBlob] = useState<Blob | null>(null);
  const [temporalBlobs, setTemporalBlobs] = useState<Blob[]>([]);
  const [isCapturing, setIsCapturing] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const stopCamera = () => {
    setStream((prevStream) => {
      if (prevStream) {
        prevStream.getTracks().forEach(track => track.stop());
      }
      return null;
    });
  };

  const startCamera = async () => {
    setErrorMsg(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err: any) {
      if (err.name === 'NotAllowedError') {
        setErrorMsg("Camera access was denied. Please allow camera access in your browser settings.");
      } else if (err.name === 'NotFoundError') {
        setErrorMsg("No compatible camera was detected.");
      } else {
        setErrorMsg("Camera access is required for live KYC capture.");
      }
    }
  };

  const captureFrame = (video: HTMLVideoElement, canvas: HTMLCanvasElement): Promise<Blob | null> => {
    return new Promise((resolve) => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => resolve(blob), 'image/jpeg', 0.8);
      } else {
        resolve(null);
      }
    });
  };

  const handleCapture = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    setIsCapturing(true);
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const frames: Blob[] = [];
    
    // Capture the primary frame first
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
      setCapturedImage(dataUrl);
      
      canvas.toBlob((blob) => {
        if (blob) setCapturedBlob(blob);
      }, 'image/jpeg', 0.9);
    }
    
    // Capture ~12 frames over ~1.2 seconds
    for (let i = 0; i < 12; i++) {
      const blob = await captureFrame(video, canvas);
      if (blob) frames.push(blob);
      await new Promise(r => setTimeout(r, 100)); // 100ms interval
    }
    
    setTemporalBlobs(frames);
    setIsCapturing(false);
    stopCamera();
  };

  const handleRetake = () => {
    setCapturedImage(null);
    setCapturedBlob(null);
    setTemporalBlobs([]);
    startCamera();
  };

  const handleAnalyze = async () => {
    if (!capturedBlob) return;
    
    setIsAnalyzing(true);
    try {
      const file = new File([capturedBlob], "live-capture.jpg", { type: "image/jpeg" });
      const temporalFiles = temporalBlobs.map((blob, i) => new File([blob], `frame_${i}.jpg`, { type: "image/jpeg" }));
      const result = await detectImage(file, temporalFiles);
      onResult(result);
    } catch (err: any) {
      onError(err.message || "Failed to analyze captured image");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="live-camera-container" style={{ padding: '2rem 0' }}>
      <div className="text-center" style={{ marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: '#e2e8f0', letterSpacing: '0.05em' }}>LIVE KYC VERIFICATION</h3>
        <p className="subtitle" style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Position the document/face clearly inside the camera frame.</p>
      </div>

      {errorMsg ? (
        <div className="error-banner" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)', maxWidth: '640px', margin: '0 auto' }}>
          <AlertCircle size={20} />
          <span>{errorMsg}</span>
        </div>
      ) : (
        <div className="camera-wrapper" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          
          {!capturedImage ? (
            <>
              <div className="video-frame" style={{ border: '2px solid #334155', borderRadius: '12px', overflow: 'hidden', marginBottom: '1.5rem', background: '#0f172a', width: '100%', maxWidth: '640px', aspectRatio: '4/3', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <video 
                  ref={videoRef} 
                  autoPlay 
                  playsInline 
                  muted 
                  style={{ width: '100%', height: '100%', objectFit: 'cover', display: stream ? 'block' : 'none' }}
                />
                {!stream && <span style={{ color: '#64748b' }}>Loading camera...</span>}
              </div>
              <button className="primary-button" onClick={handleCapture} disabled={!stream || isCapturing} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Camera size={18} /> 
                {isCapturing ? "Capturing sequence..." : "Capture Image"}
              </button>
            </>
          ) : (
            <>
              <div className="video-frame" style={{ border: '2px solid #334155', borderRadius: '12px', overflow: 'hidden', marginBottom: '1.5rem', background: '#0f172a', width: '100%', maxWidth: '640px' }}>
                <img 
                  src={capturedImage} 
                  alt="Captured frame" 
                  style={{ width: '100%', height: 'auto', display: 'block' }}
                />
              </div>
              
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button className="secondary-button" onClick={handleRetake} disabled={isAnalyzing} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <RefreshCw size={18} />
                  Retake
                </button>
                <button className="primary-button" onClick={handleAnalyze} disabled={isAnalyzing} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Check size={18} />
                  {isAnalyzing ? "Analyzing..." : "Analyze"}
                </button>
              </div>
            </>
          )}
          
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
      )}
    </div>
  );
};

export default LiveCameraCapture;
