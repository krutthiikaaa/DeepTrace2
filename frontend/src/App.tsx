import { useState } from 'react';
import BackendStatus from './components/BackendStatus';
import DetectionTabs from './components/DetectionTabs';
import MediaUploader from './components/MediaUploader';
import ResultDisplay from './components/ResultDisplay';
import type { DetectionResult } from './types/detection';
import { AlertCircle } from 'lucide-react';

function App() {
  const [mode, setMode] = useState<'image' | 'video' | 'audio'>('image');
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleModeChange = (newMode: 'image' | 'video' | 'audio') => {
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
          <h1>DeepTrace: KYC Media Authenticity & Risk Analyzer</h1>
          <BackendStatus />
        </div>
      </header>

      <main className="main-content">
        <div className="detection-panel">
          <DetectionTabs 
            activeMode={mode} 
            onModeChange={handleModeChange} 
            disabled={false} // Would disable if analyzing
          />
          
          <div className="panel-body">
            {error && (
              <div className="error-banner">
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
            )}
            
            {!result ? (
              <MediaUploader 
                mode={mode} 
                onResult={handleResult} 
                onError={handleError} 
              />
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
        </div>
      </main>
    </div>
  );
}

export default App;
