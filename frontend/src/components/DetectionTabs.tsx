import React from 'react';
import { Image, Video, Mic, Camera } from 'lucide-react';

interface Props {
  activeMode: 'image' | 'video' | 'audio' | 'live-camera';
  onModeChange: (mode: 'image' | 'video' | 'audio' | 'live-camera') => void;
  disabled: boolean;
}

const DetectionTabs: React.FC<Props> = ({ activeMode, onModeChange, disabled }) => {
  return (
    <div className="analysis-source-section">
      <h3 className="section-title">Analysis Source</h3>
      <div className="source-cards">
        <button 
          className={`source-card ${activeMode === 'live-camera' ? 'active' : ''}`}
          onClick={() => !disabled && onModeChange('live-camera')}
          disabled={disabled}
        >
          <div className="source-card-header">
            <Camera size={20} />
            LIVE CAMERA
          </div>
          <p>Direct capture & verification</p>
        </button>
        <button 
          className={`source-card ${activeMode === 'image' ? 'active' : ''}`}
          onClick={() => !disabled && onModeChange('image')}
          disabled={disabled}
        >
          <div className="source-card-header">
            <Image size={20} />
            IMAGE
          </div>
          <p>Upload KYC photo</p>
        </button>
        <button 
          className={`source-card ${activeMode === 'video' ? 'active' : ''}`}
          onClick={() => !disabled && onModeChange('video')}
          disabled={disabled}
        >
          <div className="source-card-header">
            <Video size={20} />
            VIDEO
          </div>
          <p>Analyze video clip</p>
        </button>
        <button 
          className={`source-card ${activeMode === 'audio' ? 'active' : ''}`}
          onClick={() => !disabled && onModeChange('audio')}
          disabled={disabled}
        >
          <div className="source-card-header">
            <Mic size={20} />
            AUDIO
          </div>
          <p>Analyze voice print</p>
        </button>
      </div>
    </div>
  );
};

export default DetectionTabs;
