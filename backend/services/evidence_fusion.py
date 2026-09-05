import logging

logger = logging.getLogger(__name__)

# Heuristic / Operational Thresholds for Evidence Interpretation
# These are operational heuristics only.
# Not scientifically calibrated probabilities.
ELA_ANOMALY_THRESHOLD = 0.05
NOISE_ANOMALY_THRESHOLD = 0.10
FFT_HIGH_FREQ_THRESHOLD = 1.2
EYE_ALIGNMENT_THRESHOLD = 0.05
EYE_BRIGHTNESS_THRESHOLD = 0.15

def evaluate_ela(ela_data) -> dict:
    if not ela_data or not ela_data.get('available'):
        return {"source": "ELA", "status": "UNAVAILABLE", "message": "ELA forensic analysis was unavailable.", "supports_risk": None}
    
    ratio = ela_data.get('anomaly_ratio', 0)
    if ratio > ELA_ANOMALY_THRESHOLD:
        return {"source": "ELA", "status": "POSSIBLE_ANOMALY", "message": "Possible compression anomaly detected.", "supports_risk": True}
    return {"source": "ELA", "status": "NO_CLEAR_ANOMALY", "message": "No clear compression anomaly was identified.", "supports_risk": False}

def evaluate_noise(noise_data) -> dict:
    if not noise_data or not noise_data.get('available'):
        return {"source": "NOISE", "status": "UNAVAILABLE", "message": "Noise/residual analysis was unavailable.", "supports_risk": None}
    
    ratio = noise_data.get('anomaly_ratio', 0)
    if ratio > NOISE_ANOMALY_THRESHOLD:
        return {"source": "NOISE", "status": "POSSIBLE_ANOMALY", "message": "Possible residual anomaly detected.", "supports_risk": True}
    return {"source": "NOISE", "status": "NO_CLEAR_ANOMALY", "message": "No clear residual anomaly was identified.", "supports_risk": False}

def evaluate_fft(fft_data) -> dict:
    if not fft_data or not fft_data.get('available'):
        return {"source": "FFT", "status": "UNAVAILABLE", "message": "Frequency-domain analysis was unavailable.", "supports_risk": None}
    
    hfr = fft_data.get('high_frequency_ratio', 0)
    if hfr > FFT_HIGH_FREQ_THRESHOLD:
        return {"source": "FFT", "status": "POSSIBLE_ANOMALY", "message": "Possible frequency-domain anomaly detected.", "supports_risk": True}
    return {"source": "FFT", "status": "NO_CLEAR_ANOMALY", "message": "No clear frequency-domain anomaly was identified.", "supports_risk": False}

def evaluate_face_eye(face_data) -> dict:
    if not face_data or not face_data.get('available') or not face_data.get('both_eyes_detected'):
        return {"source": "FACE_EYE", "status": "UNAVAILABLE", "message": "Face/eye consistency analysis was unavailable.", "supports_risk": None}
    
    eye_stats = face_data.get('eye_analysis', {})
    if not eye_stats.get('available'):
        return {"source": "FACE_EYE", "status": "UNAVAILABLE", "message": "Eye analysis metrics were unavailable.", "supports_risk": None}
    
    align_diff = eye_stats.get('eye_center_alignment_difference', 0)
    bright_diff = eye_stats.get('brightness_difference', 0)
    
    if align_diff > EYE_ALIGNMENT_THRESHOLD or bright_diff > EYE_BRIGHTNESS_THRESHOLD:
        return {"source": "FACE_EYE", "status": "POSSIBLE_INCONSISTENCY", "message": "Possible facial consistency anomaly detected.", "supports_risk": True}
    return {"source": "FACE_EYE", "status": "CONSISTENT", "message": "No clear facial consistency anomalies were identified.", "supports_risk": False}

def perform_evidence_fusion(prediction: str, confidence: float, forensics: dict) -> dict:
    """
    Evaluates available forensic evidence and combines it with the AI prediction
    to provide a transparent KYC Risk Assessment.
    """
    
    # 1. Evaluate AI Signal Strength
    if confidence >= 0.80:
        strength = "STRONG"
    elif confidence >= 0.60:
        strength = "MODERATE"
    else:
        strength = "WEAK"
        
    ai_item = {
        "source": "AI_DETECTOR",
        "status": f"{strength}_SIGNAL",
        "message": f"The AI detector reports a {strength.lower()} {prediction.lower()}-image signal.",
        "supports_risk": (prediction == "FAKE")
    }
    
    # 2. Evaluate Forensic Modules
    ela_item = evaluate_ela(forensics.get('ela'))
    noise_item = evaluate_noise(forensics.get('noise'))
    fft_item = evaluate_fft(forensics.get('fft'))
    face_item = evaluate_face_eye(forensics.get('face_eye'))
    
    forensic_items = [ela_item, noise_item, fft_item, face_item]
    evidence_items = [ai_item] + forensic_items
    
    # 3. Aggregate Support from Forensic Signals ONLY
    supporting_signals = 0
    conflicting_signals = 0
    unavailable_signals = 0
    
    for item in forensic_items:
        if item["status"] == "UNAVAILABLE":
            unavailable_signals += 1
        elif item["status"] in ["POSSIBLE_ANOMALY", "POSSIBLE_INCONSISTENCY"]:
            if prediction == "FAKE":
                supporting_signals += 1
            else:
                conflicting_signals += 1
        else: # NO_CLEAR_ANOMALY or CONSISTENT
            if prediction == "REAL":
                supporting_signals += 1
            else:
                # FAKE prediction but clean forensics is NOT a direct contradiction, just absence of anomaly
                # So we don't count it as a conflicting_signal. It's neutral/unsupported.
                pass

    # 4. Determine Signal Agreement
    if prediction == "FAKE":
        if strength == "STRONG" and supporting_signals >= 2 and conflicting_signals == 0:
            agreement = "STRONG_SUPPORT"
        elif supporting_signals > 0:
            agreement = "MODERATE_SUPPORT"
        elif unavailable_signals == len(forensic_items):
            agreement = "INSUFFICIENT_EVIDENCE"
        else:
            agreement = "MIXED"
    else: # REAL
        if strength == "STRONG" and conflicting_signals == 0 and supporting_signals > 0:
            agreement = "STRONG_SUPPORT"
        elif conflicting_signals > 0:
            agreement = "MIXED"
        elif unavailable_signals == len(forensic_items):
            agreement = "INSUFFICIENT_EVIDENCE"
        else:
            agreement = "MODERATE_SUPPORT"

    # 5. Operational Risk Level Decision Logic
    risk_level = "REVIEW_REQUIRED"
    
    if prediction == "FAKE":
        if strength == "STRONG" and supporting_signals >= 2 and conflicting_signals == 0:
            risk_level = "HIGH_RISK"
        else:
            risk_level = "REVIEW_REQUIRED"
    else: # REAL
        if strength == "STRONG" and conflicting_signals == 0 and unavailable_signals < len(forensic_items):
            risk_level = "LOW_RISK"
        else:
            risk_level = "REVIEW_REQUIRED"

    review_recommended = (risk_level != "LOW_RISK")
    
    # 6. Generate Dynamic Explanation
    explanation_parts = []
    
    if prediction == "FAKE":
        if strength == "STRONG":
            explanation_parts.append("The AI detector reports a strong synthetic-media signal.")
        elif strength == "MODERATE":
            explanation_parts.append("The AI detector reports a moderate synthetic-media signal.")
        else:
            explanation_parts.append("The AI detector reports a weak/uncertain synthetic-media signal.")
    else:
        if strength == "STRONG":
            explanation_parts.append("The AI detector reports a strong real-image signal.")
        elif strength == "MODERATE":
            explanation_parts.append("The AI detector reports a moderate real-image signal.")
        else:
            explanation_parts.append("The AI detector reports a weak real-image signal.")
            
    anomaly_sources = [item["source"] for item in forensic_items if item["status"] in ["POSSIBLE_ANOMALY", "POSSIBLE_INCONSISTENCY"]]
    clean_sources = [item["source"] for item in forensic_items if item["status"] in ["NO_CLEAR_ANOMALY", "CONSISTENT"]]
    unavailable_sources = [item["source"] for item in forensic_items if item["status"] == "UNAVAILABLE"]
    
    if prediction == "FAKE":
        if anomaly_sources:
            explanation_parts.append(f"Forensic modules ({', '.join(anomaly_sources)}) provide additional possible anomalies.")
        if clean_sources:
            explanation_parts.append(f"Forensic modules ({', '.join(clean_sources)}) show no clear anomaly.")
        if unavailable_sources:
            explanation_parts.append(f"Modules ({', '.join(unavailable_sources)}) were unavailable.")
            
        if risk_level == "HIGH_RISK":
            explanation_parts.append("The available evidence supports elevated risk, but automated authenticity cannot be guaranteed.")
        else:
            explanation_parts.append("The available forensic evidence is insufficient or mixed. Manual KYC review is recommended.")
            
    else: # REAL
        if anomaly_sources:
            explanation_parts.append(f"However, forensic modules ({', '.join(anomaly_sources)}) detected possible anomalies.")
        elif clean_sources:
            explanation_parts.append("The available forensic checks show no clear anomalies.")
            
        if unavailable_sources == len(forensic_items):
            explanation_parts.append("All forensic modules are unavailable.")
            
        if risk_level == "LOW_RISK":
            explanation_parts.append("This does not guarantee authenticity; automated analysis should be treated as supporting evidence.")
        else:
            explanation_parts.append("The available forensic evidence is insufficient or mixed. Manual KYC review is recommended.")
            
    explanation = " ".join(explanation_parts)
    
    return {
        "risk_level": risk_level,
        "overall_status": risk_level,
        "signal_agreement": agreement,
        "review_recommended": review_recommended,
        "ai_signal": {
            "prediction": prediction,
            "confidence": confidence,
            "strength": strength
        },
        "evidence_summary": {
            "supporting_signals": supporting_signals,
            "conflicting_signals": conflicting_signals,
            "unavailable_signals": unavailable_signals
        },
        "evidence_items": evidence_items,
        "explanation": explanation
    }
