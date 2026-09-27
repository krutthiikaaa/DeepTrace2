import React from 'react';
import { Image, Video, Mic, Camera } from 'lucide-react';

interface Props {
  activeMode: 'image' | 'video' | 'audio' | 'live-camera';
  onModeChange: (mode: 'image' | 'video' | 'audio' | 'live-camera') => void;
  disabled: boolean;
}

const DetectionTabs: React.FC<Props> = ({ activeMode, onModeChange, disabled }) => {
  return (
    <div className="tabs-container">
      <button 
        className={`tab-btn ${activeMode === 'live-camera' ? 'active' : ''}`}
        onClick={() => !disabled && onModeChange('live-camera')}
        disabled={disabled}
      >
        <Camera size={18} />
        Live Camera
      </button>
      <button 
        className={`tab-btn ${activeMode === 'image' ? 'active' : ''}`}
        onClick={() => !disabled && onModeChange('image')}
        disabled={disabled}
      >
        <Image size={18} />
        Image Upload
      </button>
      <button 
        className={`tab-btn ${activeMode === 'video' ? 'active' : ''}`}
        onClick={() => !disabled && onModeChange('video')}
        disabled={disabled}
      >
        <Video size={18} />
        Video
      </button>
      <button 
        className={`tab-btn ${activeMode === 'audio' ? 'active' : ''}`}
        onClick={() => !disabled && onModeChange('audio')}
        disabled={disabled}
      >
        <Mic size={18} />
        Audio
      </button>
    </div>
  );
};

export default DetectionTabs;
