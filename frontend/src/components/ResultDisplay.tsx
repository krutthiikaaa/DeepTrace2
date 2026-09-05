import React from 'react';
import { DetectionResult, VideoDetectionResult } from '../types/detection';
import { ShieldAlert, ShieldCheck } from 'lucide-react';
import ImageReport from './ImageReport';
import { ImageDetectionResult } from '../types/detection';

interface Props {
  result: DetectionResult | null;
}

const ResultDisplay: React.FC<Props> = ({ result }) => {
  if (!result) return null;

  if (result.media_type === 'image') {
    return <ImageReport result={result as ImageDetectionResult} />;
  }

  const isReal = result.prediction === 'REAL';

  return (
    <div className="result-card">
      <div className={`prediction-banner ${isReal ? 'real' : 'fake'}`}>
        {isReal ? <ShieldCheck size={32} /> : <ShieldAlert size={32} />}
        <h2>{result.prediction}</h2>
      </div>

      <div className="result-details">
        <div className="detail-row">
          <span className="label">Confidence</span>
          <span className="value">{(result.confidence * 100).toFixed(2)}%</span>
        </div>
        <div className="detail-row">
          <span className="label">Media Type</span>
          <span className="value uppercase">{result.media_type}</span>
        </div>

        {result.media_type === 'video' && (
          <>
            <div className="detail-row">
              <span className="label">Frames Analyzed</span>
              <span className="value">{(result as VideoDetectionResult).frames_analyzed}</span>
            </div>
            <div className="detail-row">
              <span className="label">Avg Real Score</span>
              <span className="value">{((result as VideoDetectionResult).real_score_mean * 100).toFixed(2)}%</span>
            </div>
            <div className="detail-row">
              <span className="label">Avg Fake Score</span>
              <span className="value">{((result as VideoDetectionResult).fake_score_mean * 100).toFixed(2)}%</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ResultDisplay;
