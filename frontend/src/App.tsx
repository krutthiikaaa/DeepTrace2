import { useState } from 'react';
import BackendStatus from './components/BackendStatus';
import DetectionTabs from './components/DetectionTabs';
import MediaUploader from './components/MediaUploader';
import LiveCameraCapture from './components/LiveCameraCapture';
import ResultDisplay from './components/ResultDisplay';
import type { DetectionResult } from './types/detection';
import { AlertCircle, ShieldAlert } from 'lucide-react';

function App() {
  const [mode, setMode] = useState<'image' | 'video' | 'audio' | 'live-camera' | null>(null);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleModeChange = (newMode: 'image' | 'video' | 'audio' | 'live-camera') => {
    setMode(newMode);
    setResult(null);
    setError(null);
  };

  const handleResult = (res: DetectionResult) => {
    setResult(res);
    setError(null);
  };

  const handleError = (msg: string) => {
    setError(msg);
    setResult(null);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title-container">
            <h1>DeepTrace</h1>
            <span className="header-subtitle">KYC Media Authenticity & Risk Analyzer</span>
          </div>
          <BackendStatus />
        </div>
      </header>

      <main className="main-content">
        <div className="intro-section">
          <div className="intro-title">DeepTrace Verification Platform</div>
          <h2 className="intro-heading">Forensic Media Analysis</h2>
          <p className="intro-desc">
            Analyze submitted media for AI-generation, manipulation, forensic anomalies, and capture-integrity risks.
          </p>
          <div className="intro-badges">
            <span className="intro-badge">AI Detection</span>
            <span className="intro-badge">Digital Forensics</span>
            <span className="intro-badge">Capture Integrity</span>
            <span className="intro-badge">Explainable Review</span>
          </div>
        </div>

        <DetectionTabs 
          activeMode={mode || 'image'} 
          onModeChange={handleModeChange} 
          disabled={false}
        />
        
        {error && (
          <div className="error-banner">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}
        
        <div className="input-workspace">
          {!result ? (
            mode === 'live-camera' ? (
              <LiveCameraCapture 
                onResult={handleResult} 
                onError={handleError} 
              />
            ) : mode ? (
              <MediaUploader 
                mode={mode} 
                onResult={handleResult} 
                onError={handleError} 
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                <ShieldAlert size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
                <h3>Choose how you want to provide the media</h3>
                <p>Select an analysis source above to begin</p>
              </div>
            )
          ) : (
            <div className="result-container">
              <ResultDisplay result={result} />
              <button 
                className="secondary-button mt-4" 
                onClick={() => setResult(null)}
              >
                Analyze Another {mode}
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
