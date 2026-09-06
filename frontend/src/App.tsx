import { useState, useEffect } from 'react';
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
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Revoke the previous preview URL whenever it's replaced or on unmount.
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleModeChange = (newMode: 'image' | 'video' | 'audio') => {
    setMode(newMode);
    setResult(null);
    setError(null);
    setPreviewUrl(null);
  };

  const handleResult = (res: DetectionResult, sourceFile: File) => {
    setResult(res);
    setError(null);
    setPreviewUrl(URL.createObjectURL(sourceFile));
  };

  const handleError = (msg: string) => {
    setError(msg);
    setResult(null);
  };

  const handleReset = () => {
    setResult(null);
    setPreviewUrl(null);
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
        <div className={`detection-panel ${result?.media_type === 'image' ? 'detection-panel--wide' : ''}`}>
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
                <ResultDisplay result={result} previewUrl={previewUrl} />
                <button
                  className="secondary-button mt-4"
                  onClick={handleReset}
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
