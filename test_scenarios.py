import sys
import json
sys.path.append('c:\\Users\\karthikeya\\Desktop\\DeepTrace2\\DeepTrace2')
from backend.services.evidence_fusion import perform_evidence_fusion

def simulate(ai_pred, ai_conf, ela_val, noise_val, fft_val, face_val):
    forensics = {}
    if ela_val == 'anomaly': forensics['ela'] = {'available': True, 'anomaly_ratio': 1.0}
    elif ela_val == 'clean': forensics['ela'] = {'available': True, 'anomaly_ratio': 0.0}
    else: forensics['ela'] = {'available': False}

    if noise_val == 'anomaly': forensics['noise'] = {'available': True, 'anomaly_ratio': 1.0}
    elif noise_val == 'clean': forensics['noise'] = {'available': True, 'anomaly_ratio': 0.0}
    else: forensics['noise'] = {'available': False}

    if fft_val == 'anomaly': forensics['fft'] = {'available': True, 'high_frequency_ratio': 2.0}
    elif fft_val == 'clean': forensics['fft'] = {'available': True, 'high_frequency_ratio': 1.0}
    else: forensics['fft'] = {'available': False}

    if face_val == 'consistent': forensics['face_eye'] = {'available': True, 'both_eyes_detected': True, 'eye_analysis': {'available': True, 'eye_center_alignment_difference': 0.0, 'brightness_difference': 0.0}}
    else: forensics['face_eye'] = {'available': False}

    return perform_evidence_fusion(ai_pred, ai_conf, forensics)

tests = [
    ('Test A', 'FAKE', 0.85, 'anomaly', 'anomaly', 'anomaly', 'unavailable'),
    ('Test B', 'FAKE', 0.85, 'anomaly', 'unavailable', 'unavailable', 'unavailable'),
    ('Test C', 'FAKE', 0.65, 'anomaly', 'anomaly', 'clean', 'unavailable'),
    ('Test D', 'FAKE', 0.55, 'unavailable', 'unavailable', 'unavailable', 'unavailable'),
    ('Test E', 'REAL', 0.85, 'clean', 'clean', 'clean', 'consistent'),
    ('Test F', 'REAL', 0.85, 'anomaly', 'anomaly', 'unavailable', 'unavailable'),
    ('Test G', 'REAL', 0.85, 'unavailable', 'unavailable', 'unavailable', 'unavailable')
]

for name, p, c, e, n, f, fa in tests:
    res = simulate(p, c, e, n, f, fa)
    print(f"{name}: {res['risk_level']} | Supp: {res['evidence_summary']['supporting_signals']} | Conf: {res['evidence_summary']['conflicting_signals']} | Unav: {res['evidence_summary']['unavailable_signals']}")
