import React, { useState, useRef } from 'react';
import { X, Loader2, FileAudio, FileVideo, FileImage } from 'lucide-react';
import type { DetectionResult } from '../types/detection';
import { detectImage, detectVideo, detectAudio } from '../services/api';

interface Props {
  mode: 'image' | 'video' | 'audio';
  onResult: (result: DetectionResult) => void;
  onError: (msg: string) => void;
}

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

const MediaUploader: React.FC<Props> = ({ mode, onResult, onError }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

      if (result) onResult(result);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getAcceptType = () => {
    if (mode === 'image') return 'image/jpeg, image/png';
    if (mode === 'video') return 'video/*';
    if (mode === 'audio') return 'audio/wav'; 
    return '*/*';
  };

  const getIcon = () => {
    if (mode === 'image') return <FileImage size={48} className="upload-icon" />;
    if (mode === 'video') return <FileVideo size={48} className="upload-icon" />;
    return <FileAudio size={48} className="upload-icon" />;
  };

  if (isAnalyzing) {
    return (
      <div className="analyzing">
        <Loader2 className="spinner" size={48} />
        <h3 className="pulse-text">
          {mode === 'image' ? 'ANALYZING KYC MEDIA' : `ANALYZING ${mode.toUpperCase()} MEDIA`}
        </h3>
        <p className="subtitle">
          Running AI detection and forensic analysis...
        </p>
      </div>
    );
  }

  return (
    <div className="upload-container">
      {!file ? (
        <label className="upload-dropzone">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept={getAcceptType()}
            className="hidden-input"
          />
          {getIcon()}
          <h3>UPLOAD KYC {mode.toUpperCase()}</h3>
          <p className="subtitle">Drop {mode === 'image' ? 'an image' : `a ${mode}`} here or browse from your device</p>
          <p className="subtitle" style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>Supported: {mode === 'image' ? 'JPEG / PNG' : mode === 'audio' ? 'WAV' : 'Video'}<br/>Maximum 50 MB</p>
        </label>
      ) : (
        <div className="two-column-layout">
          <div className="left-col">
            <h4 className="section-title">Media Preview</h4>
            {mode === 'image' && file ? (
              <div style={{ border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden' }}>
                <img
                  src={URL.createObjectURL(file)}
                  alt="Selected KYC"
                  style={{ width: '100%', height: 'auto', display: 'block', maxHeight: '400px', objectFit: 'contain', background: '#f8fafc' }}
                />
              </div>
            ) : (
              <div style={{ border: '1px solid var(--border)', borderRadius: '8px', background: '#f8fafc', padding: '4rem', display: 'flex', justifyContent: 'center' }}>
                {getIcon()}
              </div>
            )}
          </div>
          <div className="right-col">
            <div className="selected-file-card">
              <h4 className="section-title">File Information</h4>
              <div className="file-info">
                <div className="file-details">
                  <h4>{file.name}</h4>
                  <p>{file.type || 'Unknown type'} • {(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
                <button onClick={clearFile} className="icon-button" title="Remove file">
                  <X size={20} />
                </button>
              </div>
              <button className="primary-button" onClick={startAnalysis}>
                Analyze {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaUploader;
