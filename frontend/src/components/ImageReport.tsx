import React from 'react';
import type { ImageDetectionResult } from '../types/detection';
import ForensicEvidence from './ForensicEvidence';
import { AlertTriangle, Info, CheckCircle, Search, FileSearch } from 'lucide-react';

interface Props {
  result: ImageDetectionResult;
}

const ImageReport: React.FC<Props> = ({ result }) => {
  const risk = result.risk_assessment;
  
  if (!risk) {
    return (
      <div className="report-fallback">
        <p>Risk assessment unavailable. Displaying raw output.</p>
        <div className="detail-row"><span className="label">Prediction</span><span className="value">{result.prediction}</span></div>
        <div className="detail-row"><span className="label">Confidence</span><span className="value">{(result.confidence * 100).toFixed(2)}%</span></div>
        <ForensicEvidence result={result} />
      </div>
    );
  }

  // Formatting risk level string
  const getRiskTitle = (level: string) => {
    return level.replace(/_/g, ' ');
  };

  // Determining Risk UI
  const isHigh = risk.risk_level === 'HIGH_RISK';
  const isLow = risk.risk_level === 'LOW_RISK';

  let riskIcon = <Info size={32} />;
  if (isHigh) riskIcon = <AlertTriangle size={32} />;
  if (isLow) riskIcon = <CheckCircle size={32} />;

  let riskExpl = "Available evidence is insufficient or conflicting. Manual verification is recommended.";
  if (isHigh) riskExpl = "Strong AI-generated/manipulation signal with supporting forensic anomalies. Manual verification is recommended.";
  if (isLow) riskExpl = "Strong real-image signal with no conflicting forensic anomalies detected by the available checks.";

  let rec = "Manual verification recommended because the available evidence is insufficient or conflicting.";
  if (isHigh) rec = "Do not rely on automated approval alone. Perform manual KYC verification and request additional verification evidence if required.";
  if (isLow) rec = "No significant conflicting forensic evidence was detected by the available checks. Continue with normal KYC verification procedures.";
  
  if (result.capture_integrity?.status === 'POSSIBLE_RECAPTURE') {
    rec = "Manual verification recommended because the capture medium may be re-presented.";
  }

  return (
    <div className="kyc-report">
      {/* 2. Overall Risk Decision */}
      <div className={`risk-decision-card ${risk.risk_level.toLowerCase()}`}>
        <div className="risk-title">
          {riskIcon}
          <h3>{getRiskTitle(risk.risk_level)}</h3>
        </div>
        <p className="risk-desc">{riskExpl}</p>
      </div>

      <div className="dashboard-grid">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Capture Integrity Section */}
          {result.capture_integrity && result.capture_integrity.status !== 'UNAVAILABLE' && (
            <div className="dashboard-card">
              <div className="card-heading">
                <Info size={18} />
                <h4>CAPTURE INTEGRITY</h4>
              </div>
              <div className="card-content">
                <div className="capture-integrity-status">
                  {getRiskTitle(result.capture_integrity.status)}
                </div>
                
                {result.capture_integrity.indicators && result.capture_integrity.indicators.length > 0 ? (
                  <div style={{ marginTop: '1rem' }}>
                    <span className="stat-label" style={{ fontWeight: '600', marginBottom: '0.5rem', display: 'block' }}>Indicators:</span>
                    <ul className="capture-indicators">
                      {result.capture_integrity.indicators.map((ind, idx) => (
                        <li key={idx}>✓ {ind}</li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div style={{ marginTop: '1rem' }}>
                    <span className="stat-label" style={{ fontWeight: '600', marginBottom: '0.5rem', display: 'block' }}>Indicators:</span>
                    <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-muted)' }}>No clear display/re-presentation indicators detected.</p>
                  </div>
                )}

                <div style={{ marginTop: '1rem' }}>
                  <p className="capture-explanation">
                    {result.capture_integrity.status === 'POSSIBLE_RECAPTURE' 
                      ? "The camera captured evidence consistent with a previously displayed or reproduced image. This does not prove that the underlying content is manipulated, but direct authenticity assessment may be unreliable."
                      : result.capture_integrity.explanation}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* 3. AI Detection */}
          <div className="dashboard-card">
            <div className="card-heading">
              <Search size={18} />
              <h4>AI DETECTION</h4>
            </div>
            <div className="card-content ai-stats">
              <div className="stat-box border-bottom">
                <span className="stat-label">Prediction</span>
                <span className={`stat-value ${result.prediction === 'REAL' ? 'real-text' : 'fake-text'}`}>
                  {result.prediction}
                </span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Confidence</span>
                <span className="stat-value">
                  {result.confidence !== undefined ? `${(result.confidence * 100).toFixed(0)}%` : 'Unavailable'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* 4. Why This Decision? */}
          <div className="dashboard-card">
            <div className="card-heading">
              <FileSearch size={18} />
              <h4>WHY THIS DECISION?</h4>
            </div>
            <p style={{ fontSize: '1rem', lineHeight: 1.6 }}>{risk.explanation || "Additional explanation is unavailable. Review the available evidence below."}</p>
            
            {/* 7. Evidence Items List (Compact) */}
            {risk.evidence_items && risk.evidence_items.length > 0 && (
              <ul className="evidence-list" style={{ marginTop: '1rem' }}>
                {risk.evidence_items.filter(item => item.source !== 'AI_DETECTOR').map((item, idx) => {
                  const icon = item.status === 'UNAVAILABLE' ? '—' : '✓';
                  const cleanStatus = item.status.replace(/_/g, ' ').toLowerCase();
                  return (
                    <li key={idx}>
                      <span className="item-icon">{icon}</span>
                      <div className="evidence-content">
                        <span className="item-status">{item.source.replace(/_/g, ' ')} — {cleanStatus}</span>
                        <span className="item-msg">{item.message}</span>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
          
          {/* 8. Reviewer Recommendation */}
          <div className="reviewer-recommendation">
            <h4>REVIEWER RECOMMENDATION</h4>
            <p>{rec}</p>
          </div>
        </div>
      </div>

      {/* 6. Forensic Evidence (Phase 10 visualization) */}
      <div className="forensic-wrapper" style={{ marginTop: '1rem' }}>
        <ForensicEvidence result={result} />
      </div>

      {/* 9. Disclaimer */}
      <div className="kyc-disclaimer">
        <p>This analysis assesses the authenticity characteristics of the uploaded media. It does not independently verify the person's identity or guarantee that the document/selfie belongs to the claimed individual.</p>
      </div>
    </div>
  );
};

export default ImageReport;
