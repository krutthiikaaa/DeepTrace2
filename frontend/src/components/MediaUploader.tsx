import React, { useState, useRef, useEffect } from 'react';
import { X, Loader2, FileAudio, FileVideo, FileImage, Camera } from 'lucide-react';
import type { DetectionResult } from '../types/detection';
import { detectImage, detectVideo, detectAudio } from '../services/api';
import WebcamCapture from './WebcamCapture';

interface Props {
  mode: 'image' | 'video' | 'audio';
  onResult: (result: DetectionResult, sourceFile: File) => void;
  onError: (msg: string) => void;
}

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

const MediaUploader: React.FC<Props> = ({ mode, onResult, onError }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [source, setSource] = useState<'upload' | 'webcam'>('upload');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Leaving the Image tab always resets back to the default upload view,
  // so returning to Image later doesn't silently relaunch the camera.
  useEffect(() => {
    if (mode !== 'image') setSource('upload');
  }, [mode]);

  const handleWebcamCapture = (capturedFile: File) => {
    setFile(capturedFile);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];

      if (mode === 'image' && !['image/jpeg', 'image/png'].includes(selectedFile.type)) {
        onError("Unsupported file type. Please upload a JPG, JPEG, or PNG image.");
        if (fileInputRef.current) fileInputRef.current.value = '';
        return;
      }

      if (selectedFile.size > MAX_FILE_SIZE) {
        onError("File exceeds the 50 MB limit.");
        if (fileInputRef.current) fileInputRef.current.value = '';
        return;
      }

      setFile(selectedFile);
    }
  };

  const clearFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const startAnalysis = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    try {
      let result;
      if (mode === 'image') result = await detectImage(file);
      else if (mode === 'video') result = await detectVideo(file);
      else if (mode === 'audio') result = await detectAudio(file);

      if (result) onResult(result, file);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getAcceptType = () => {
    if (mode === 'image') return 'image/jpeg, image/png';
    if (mode === 'video') return 'video/*';
    if (mode === 'audio') return 'audio/wav'; // backend explicitly asks for WAV
    return '*/*';
  };

  const getIcon = () => {
    if (mode === 'image') return <FileImage size={48} className="upload-icon" />;
    if (mode === 'video') return <FileVideo size={48} className="upload-icon" />;
    return <FileAudio size={48} className="upload-icon" />;
  };

  if (isAnalyzing) {
    return (
      <div className="upload-container analyzing">
        <Loader2 className="spinner" size={48} />
        <h3 className="pulse-text">
          {mode === 'image' ? 'ANALYZING KYC IMAGE' : `Analyzing ${mode}...`}
        </h3>
        <p className="subtitle">
          {mode === 'image' ? 'Running AI detection and forensic analysis...' : `Please wait while the AI processes the ${mode}.`}
        </p>
      </div>
    );
  }

  return (
    <div className="upload-container">
      {mode === 'image' && !file && (
        <div className="source-toggle">
          <button
            type="button"
            className={`source-toggle-btn ${source === 'upload' ? 'active' : ''}`}
            onClick={() => setSource('upload')}
          >
            <FileImage size={16} />
            Upload Photo
          </button>
          <button
            type="button"
            className={`source-toggle-btn ${source === 'webcam' ? 'active' : ''}`}
            onClick={() => setSource('webcam')}
          >
            <Camera size={16} />
            Use Webcam
          </button>
        </div>
      )}

      {!file ? (
        mode === 'image' && source === 'webcam' ? (
          <WebcamCapture onCapture={handleWebcamCapture} onCancel={() => setSource('upload')} />
        ) : (
          <label className="upload-dropzone">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept={getAcceptType()}
              className="hidden-input"
            />
            {getIcon()}
            <h3>Select a {mode} to analyze</h3>
            <p className="subtitle">Max file size: 50MB</p>
          </label>
        )
      ) : (
        <div className="selected-file-card">
          {mode === 'image' && file ? (
            <div className="image-preview-container" style={{ textAlign: 'center', marginBottom: '1rem' }}>
              <img
                src={URL.createObjectURL(file)}
                alt="Selected KYC"
                style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '8px', objectFit: 'contain' }}
              />
            </div>
          ) : null}
          <div className="file-info">
            {mode !== 'image' && getIcon()}
            <div className="file-details">
              <h4>{file.name}</h4>
              <p>{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
            <button onClick={clearFile} className="icon-button" title="Remove file">
              <X size={20} />
            </button>
          </div>
          <button className="primary-button" onClick={startAnalysis}>
            Analyze Image
          </button>
        </div>
      )}
    </div>
  );
};

export default MediaUploader;
