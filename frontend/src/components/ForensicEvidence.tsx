import React, { useState } from 'react';
import type { ImageDetectionResult } from '../types/detection';

interface Props {
  result: ImageDetectionResult;
}

const ForensicEvidence: React.FC<Props> = ({ result }) => {
  const [modalImage, setModalImage] = useState<string | null>(null);

  if (!result.forensics) {
    return null;
  }

  const { ela, noise, fft, face_eye } = result.forensics;
  const risk = result.risk_assessment;

  const renderStatus = (status: string | undefined) => {
    if (!status) return <span className="status-badge unavailable">Unavailable</span>;
    const cleanStatus = status.replace(/_/g, ' ').toUpperCase();
    
    let badgeClass = 'unavailable';
    if (status === 'POSSIBLE_ANOMALY' || status === 'POSSIBLE_INCONSISTENCY') badgeClass = 'anomaly';
    else if (status === 'NO_CLEAR_ANOMALY' || status === 'CONSISTENT') badgeClass = 'clear';
    
    return <span className={`status-badge ${badgeClass}`}>{cleanStatus}</span>;
  };

  // The backend currently might not directly put 'status' on the root of the forensic object unless it's in the new risk items.
  // Wait, let's map the status from the risk_assessment items since they have exactly 'POSSIBLE_ANOMALY', etc.
  const getRiskItemStatus = (sourceName: string) => {
    const item = risk?.evidence_items?.find(i => i.source === sourceName);
    return item ? item.status : 'UNAVAILABLE';
  };

  return (
    <div className="forensic-section">
      <div className="forensic-header">
        <h3>FORENSIC EVIDENCE</h3>
        <p>These forensic checks provide supporting evidence for the assessment. Individual signals are not proof of manipulation.</p>
      </div>

      <div className="forensic-grid">
        {/* ELA Card */}
        <div className="forensic-card">
          <div className="card-header">
            <h4>ELA</h4>
            <p className="description">Checks for unusual JPEG compression differences.</p>
            <div className="status-row">
              <span className="label">Status:</span>
              {renderStatus(getRiskItemStatus('ELA'))}
            </div>
          </div>
          
          <div className="card-metrics">
             {ela?.available && ela.anomaly_ratio !== undefined && (
               <div className="metric">
                 <span className="metric-label">Anomaly Ratio:</span>
                 <span className="metric-value">{(ela.anomaly_ratio * 100).toFixed(2)}%</span>
               </div>
             )}
          </div>
          
          {ela?.image ? (
            <div className="viz-container" onClick={() => setModalImage(ela.image!)}>
              <div className="viz-label">Compression Difference Map</div>
              <img src={ela.image} alt="ELA Visualization" className="viz-image" />
              <div className="expand-hint">Click to expand</div>
            </div>
          ) : (
            <div className="no-viz">No visualization available</div>
          )}
        </div>

        {/* Noise Card */}
        <div className="forensic-card">
          <div className="card-header">
            <h4>NOISE</h4>
            <p className="description">Examines image residual patterns after smoothing.</p>
            <div className="status-row">
              <span className="label">Status:</span>
              {renderStatus(getRiskItemStatus('NOISE'))}
            </div>
          </div>

          <div className="card-metrics">
             {noise?.available && noise.anomaly_ratio !== undefined && (
               <div className="metric">
                 <span className="metric-label">Anomaly Ratio:</span>
                 <span className="metric-value">{(noise.anomaly_ratio * 100).toFixed(2)}%</span>
               </div>
             )}
          </div>

          {noise?.image ? (
            <div className="viz-container" onClick={() => setModalImage(noise.image!)}>
              <div className="viz-label">Noise / Residual Map</div>
              <img src={noise.image} alt="Noise Visualization" className="viz-image" />
              <div className="expand-hint">Click to expand</div>
            </div>
          ) : (
            <div className="no-viz">No visualization available</div>
          )}
        </div>

        {/* FFT Card */}
        <div className="forensic-card">
          <div className="card-header">
            <h4>FFT</h4>
            <p className="description">Examines frequency-domain characteristics of the image.</p>
            <div className="status-row">
              <span className="label">Status:</span>
              {renderStatus(getRiskItemStatus('FFT'))}
            </div>
          </div>

          <div className="card-metrics">
             {fft?.available && fft.high_frequency_ratio !== undefined && (
               <div className="metric">
                 <span className="metric-label">High Frequency Ratio:</span>
                 <span className="metric-value">{fft.high_frequency_ratio.toFixed(3)}</span>
               </div>
             )}
          </div>

          {fft?.image ? (
            <div className="viz-container" onClick={() => setModalImage(fft.image!)}>
              <div className="viz-label">Frequency Spectrum</div>
              <img src={fft.image} alt="FFT Visualization" className="viz-image" />
              <div className="expand-hint">Click to expand</div>
            </div>
          ) : (
            <div className="no-viz">No visualization available</div>
          )}
        </div>

        {/* Face/Eye Card */}
        <div className="forensic-card">
          <div className="card-header">
            <h4>FACE & EYE</h4>
            <p className="description">Checks detected face and eye geometry for possible inconsistencies.</p>
            <div className="status-row">
              <span className="label">Status:</span>
              {renderStatus(getRiskItemStatus('FACE_EYE'))}
            </div>
          </div>

          <div className="card-metrics">
             {face_eye?.available ? (
               <>
                 {face_eye.face_count !== undefined && (
                   <div className="metric">
                     <span className="metric-label">Face Count:</span>
                     <span className="metric-value">{face_eye.face_count}</span>
                   </div>
                 )}
                 {face_eye.eye_analysis?.available && face_eye.eye_analysis.eye_center_alignment_difference !== undefined && (
                   <div className="metric">
                     <span className="metric-label">Eye Alignment Diff:</span>
                     <span className="metric-value">{(face_eye.eye_analysis.eye_center_alignment_difference * 100).toFixed(2)}%</span>
                   </div>
                 )}
               </>
             ) : (
               <div className="metric">
                 <span className="metric-value unavailable-text">Face/eye analysis could not be performed for this image.</span>
               </div>
             )}
          </div>

          {face_eye?.image ? (
            <div className="viz-container" onClick={() => setModalImage(face_eye.image!)}>
              <div className="viz-label">Face & Eye Detection Map</div>
              <img src={face_eye.image} alt="Face Eye Visualization" className="viz-image" />
              <div className="expand-hint">Click to expand</div>
            </div>
          ) : (
             <div className="no-viz">No visualization available</div>
          )}
        </div>
      </div>

      {risk?.explanation && (
        <div className="risk-explanation-box">
          <h4>Risk Assessment Summary</h4>
          <p>{risk.explanation}</p>
        </div>
      )}

      {/* Image Modal Overlay */}
      {modalImage && (
        <div className="image-modal-overlay" onClick={() => setModalImage(null)}>
          <div className="image-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setModalImage(null)}>×</button>
            <img src={modalImage} alt="Expanded Forensic View" />
          </div>
        </div>
      )}
    </div>
  );
};

export default ForensicEvidence;
