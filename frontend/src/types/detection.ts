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

export interface ImageDetectionResult extends BaseDetectionResult {
  media_type: "image";
  forensics?: {
    ela?: ELAForensics;
    noise?: NoiseForensics;
  };
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
