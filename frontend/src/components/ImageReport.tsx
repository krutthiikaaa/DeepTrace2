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
      {/* 1. KYC Analysis Header */}
      <div className="report-header text-center">
        <h2>KYC AUTHENTICITY ANALYSIS</h2>
        <p className="subtitle">Explainable analysis of the uploaded KYC image using AI detection and supporting forensic signals.</p>
      </div>

      {/* 2. Overall Risk Decision */}
      <div className={`risk-decision-card ${risk.risk_level.toLowerCase()}`}>
        <div className="risk-title">
          {riskIcon}
          <h3>{getRiskTitle(risk.risk_level)}</h3>
        </div>
        <p className="risk-desc">{riskExpl}</p>
      </div>

      <div className="report-grid">
        {/* 3. AI Detection */}
        <div className="report-card">
          <div className="card-heading">
            <Search size={18} />
            <h4>AI DETECTION</h4>
          </div>
          <div className="card-content ai-stats">
            <div className="stat-box">
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
          <p className="card-footnote">This is the output of the AI image detector and is evaluated separately from the forensic evidence.</p>
        </div>

        {/* 5. Evidence Summary */}
        <div className="report-card">
          <div className="card-heading">
            <FileSearch size={18} />
            <h4>EVIDENCE SUMMARY</h4>
          </div>
          <div className="card-content summary-stats">
            <div className="summary-row">
              <span>Supporting forensic signals</span>
              <strong>{risk.evidence_summary?.supporting_signals ?? 0}</strong>
            </div>
            <div className="summary-row">
              <span>Conflicting forensic signals</span>
              <strong>{risk.evidence_summary?.conflicting_signals ?? 0}</strong>
            </div>
            <div className="summary-row">
              <span>Unavailable checks</span>
              <strong>{risk.evidence_summary?.unavailable_signals ?? 0}</strong>
            </div>
          </div>
        </div>
        {/* Capture Integrity Section */}
        {result.capture_integrity && result.capture_integrity.status !== 'UNAVAILABLE' && (
          <div className="report-card full-width">
            <div className="card-heading">
              <Info size={18} />
              <h4>CAPTURE INTEGRITY</h4>
            </div>
            <div className="card-content">
              <div className="detail-row">
                <span className="label" style={{ fontWeight: 'bold' }}>Status:</span>
                <span className="value" style={{ fontWeight: 'bold' }}>{getRiskTitle(result.capture_integrity.status)}</span>
              </div>
              
              {result.capture_integrity.indicators && result.capture_integrity.indicators.length > 0 ? (
                <div style={{ marginTop: '1rem' }}>
                  <span className="label" style={{ fontWeight: 'bold' }}>Indicators:</span>
                  <ul style={{ margin: '0.5rem 0 0 1rem', padding: 0 }}>
                    {result.capture_integrity.indicators.map((ind, idx) => (
                      <li key={idx}>✓ {ind}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div style={{ marginTop: '1rem' }}>
                  <span className="label" style={{ fontWeight: 'bold' }}>Indicators:</span>
                  <p style={{ margin: '0.5rem 0 0 0' }}>No clear display/re-presentation indicators detected.</p>
                </div>
              )}

              <div style={{ marginTop: '1rem' }}>
                <span className="label" style={{ fontWeight: 'bold' }}>Explanation:</span>
                <p style={{ marginTop: '0.5rem', fontStyle: 'italic' }}>
                  {result.capture_integrity.status === 'POSSIBLE_RECAPTURE' 
                    ? "The camera captured evidence consistent with a previously displayed or reproduced image. This does not prove that the underlying content is manipulated, but direct authenticity assessment may be unreliable."
                    : result.capture_integrity.explanation}
                </p>
              </div>
            </div>
            <p className="card-footnote">Content authenticity and capture integrity are separate assessments.</p>
          </div>
        )}
      </div>

      {/* 4. Why This Decision? */}
      <div className="decision-explanation">
        <h4>WHY THIS DECISION?</h4>
        <p>{risk.explanation || "Additional explanation is unavailable. Review the available evidence below."}</p>
        
        {/* 7. Evidence Items List (Compact) */}
        {risk.evidence_items && risk.evidence_items.length > 0 && (
          <ul className="evidence-list">
            {risk.evidence_items.filter(item => item.source !== 'AI_DETECTOR').map((item, idx) => {
              const icon = item.status === 'UNAVAILABLE' ? '—' : '✓';
              const cleanStatus = item.status.replace(/_/g, ' ').toLowerCase();
              return (
                <li key={idx}>
                  <span className="item-icon">{icon}</span>
                  <strong>{item.source.replace(/_/g, ' ')}</strong> — <span className="item-status">{cleanStatus.charAt(0).toUpperCase() + cleanStatus.slice(1)}</span>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* 6. Forensic Evidence (Phase 10 visualization) */}
      <div className="forensic-wrapper">
        <ForensicEvidence result={result} />
      </div>

      {/* 8. Reviewer Recommendation */}
      <div className="reviewer-recommendation">
        <h4>REVIEWER RECOMMENDATION</h4>
        <p>{rec}</p>
      </div>

      {/* 9. Disclaimer */}
      <div className="kyc-disclaimer">
        <p>This analysis assesses the authenticity characteristics of the uploaded media. It does not independently verify the person's identity or guarantee that the document/selfie belongs to the claimed individual.</p>
      </div>
    </div>
  );
};

export default ImageReport;
