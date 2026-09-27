import React, { useRef, useState, useEffect } from 'react';
import { Camera, RefreshCw, Check, AlertCircle, CheckCircle2 } from 'lucide-react';
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
    <div className="live-camera-container">
      {errorMsg && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <span>{errorMsg}</span>
        </div>
      )}
      
      <div className="two-column-layout">
        <div className="left-col">
          <h4 className="section-title">Live Capture</h4>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {!capturedImage ? (
              <>
                <div style={{ border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden', background: '#0f172a', width: '100%', aspectRatio: '4/3', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <video 
                    ref={videoRef} 
                    autoPlay 
                    playsInline 
                    muted 
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: stream ? 'block' : 'none' }}
                  />
                  {!stream && <span style={{ color: '#64748b' }}>Loading camera...</span>}
                </div>
                <button className="primary-button" onClick={handleCapture} disabled={!stream || isCapturing}>
                  <Camera size={18} /> 
                  {isCapturing ? "Capturing sequence..." : "Capture Image"}
                </button>
              </>
            ) : (
              <>
                <div style={{ border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden', width: '100%', aspectRatio: '4/3' }}>
                  <img 
                    src={capturedImage} 
                    alt="Captured frame" 
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                  />
                </div>
                
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button className="secondary-button" onClick={handleRetake} disabled={isAnalyzing}>
                    <RefreshCw size={18} />
                    Retake
                  </button>
                  <button className="primary-button" onClick={handleAnalyze} disabled={isAnalyzing}>
                    <Check size={18} />
                    {isAnalyzing ? "Analyzing..." : "Analyze Image"}
                  </button>
                </div>
              </>
            )}
            <canvas ref={canvasRef} style={{ display: 'none' }} />
          </div>
        </div>

        <div className="right-col">
          <div className="guidance-card">
            <h4>KYC Capture Guidance</h4>
            <ul className="guidance-list">
              <li><CheckCircle2 size={18} /> Keep the document fully visible inside the frame</li>
              <li><CheckCircle2 size={18} /> Use even, natural lighting where possible</li>
              <li><CheckCircle2 size={18} /> Avoid harsh glare or reflections</li>
              <li><CheckCircle2 size={18} /> Capture directly from the physical document</li>
              <li><CheckCircle2 size={18} /> Do not photograph another digital screen</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveCameraCapture;
