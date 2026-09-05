export interface BaseDetectionResult {
  success: boolean;
  media_type: string;
  prediction: "REAL" | "FAKE";
  confidence: number;
}

export interface ELAForensics {
  available: boolean;
  mean?: number;
  max?: number;
  std?: number;
  anomaly_ratio?: number;
  image?: string;
  error?: string;
}

export interface NoiseForensics {
  available: boolean;
  mean?: number;
  max?: number;
  std?: number;
  anomaly_ratio?: number;
  image?: string;
  error?: string;
}

export interface FFTForensics {
  available: boolean;
  spectral_mean?: number;
  spectral_std?: number;
  high_frequency_ratio?: number;
  low_frequency_ratio?: number;
  spectral_energy?: number;
  image?: string;
  error?: string;
}

export interface EyeAnalysis {
  available: boolean;
  eye_center_alignment_difference?: number;
  eye_size_difference?: number;
  brightness_difference?: number;
}

export interface FaceEyeForensics {
  available: boolean;
  face_detected?: boolean;
  face_count?: number;
  primary_face_selected?: boolean;
  both_eyes_detected?: boolean;
  eye_analysis?: EyeAnalysis;
  image?: string;
  error?: string;
}

export type RiskLevel = "LOW_RISK" | "REVIEW_REQUIRED" | "HIGH_RISK";
export type EvidenceAgreement = "STRONG_SUPPORT" | "MODERATE_SUPPORT" | "MIXED" | "INSUFFICIENT_EVIDENCE";

export interface AISignal {
  prediction: "REAL" | "FAKE";
  confidence: number;
  strength: "STRONG" | "MODERATE" | "WEAK";
}

export interface EvidenceSummary {
  supporting_signals: number;
  conflicting_signals: number;
  unavailable_signals: number;
}

export interface EvidenceItem {
  source: string;
  status: string;
  message: string;
  supports_risk: boolean | null;
}

export interface RiskAssessment {
  risk_level: RiskLevel;
  overall_status: RiskLevel;
  signal_agreement: EvidenceAgreement;
  review_recommended: boolean;
  ai_signal: AISignal;
  evidence_summary: EvidenceSummary;
  evidence_items: EvidenceItem[];
  explanation: string;
}

export interface ImageDetectionResult extends BaseDetectionResult {
  media_type: "image";
  forensics?: {
    ela?: ELAForensics;
    noise?: NoiseForensics;
    fft?: FFTForensics;
    face_eye?: FaceEyeForensics;
  };
  risk_assessment?: RiskAssessment;
}

export interface AudioDetectionResult extends BaseDetectionResult {
  media_type: "audio";
}

export interface VideoDetectionResult extends BaseDetectionResult {
  media_type: "video";
  frames_analyzed: number;
  real_score_mean: number;
  fake_score_mean: number;
}

export type DetectionResult = ImageDetectionResult | AudioDetectionResult | VideoDetectionResult;

export interface HealthStatus {
  status: string;
  models_loaded: boolean;
}
