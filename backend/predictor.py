# predictor.py — TFLite version (LIGHTWEIGHT + Render friendly)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import numpy as np
import tensorflow as tf

# ─────────────────────────────────────────────
# 🔥 LOAD TFLITE MODEL (ONCE)
# ─────────────────────────────────────────────
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

CLASS_NAMES = ['loop', 'whorl', 'arch']
IMG_SIZE = (224, 224)
CONF_THRESH = 0.55

# ─────────────────────────────────────────────
# 🧠 STATIC DATA
# ─────────────────────────────────────────────
PATTERN_INFO = {
    'loop': {'full_name': 'Loop Pattern'},
    'whorl': {'full_name': 'Whorl Pattern'},
    'arch': {'full_name': 'Arch Pattern'}
}

_RAW = {
    'loop':  {'O+':0.28,'O-':0.08,'A+':0.22,'A-':0.06,'B+':0.16,'B-':0.05,'AB+':0.10,'AB-':0.05},
    'whorl': {'O+':0.18,'O-':0.05,'A+':0.15,'A-':0.04,'B+':0.28,'B-':0.08,'AB+':0.14,'AB-':0.08},
    'arch':  {'O+':0.18,'O-':0.06,'A+':0.22,'A-':0.08,'B+':0.12,'B-':0.04,'AB+':0.20,'AB-':0.10},
}

def _norm(d):
    t = sum(d.values())
    return {k: round(v/t, 6) for k, v in d.items()}

BG_PROBS = {k: _norm(v) for k, v in _RAW.items()}

# ─────────────────────────────────────────────
# 🛠️ IMAGE PROCESSING
# ─────────────────────────────────────────────
def _clahe(gray):
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

def _enhance(img_rgb):
    resized = cv2.resize(img_rgb, IMG_SIZE)
    enhanced = np.stack([_clahe(resized[:, :, c]) for c in range(3)], axis=-1)
    return enhanced

def _valid_fp(img_rgb):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    ratio = float(np.sum(edges > 0) / edges.size)
    return ratio >= 0.05, round(ratio, 4)

def _ridge_analysis(img_rgb):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    small = cv2.resize(gray, (128, 128))
    enh = _clahe(small)

    sx = cv2.Sobel(enh, cv2.CV_64F, 1, 0, ksize=3)
    sy = cv2.Sobel(enh, cv2.CV_64F, 0, 1, ksize=3)

    density = float(np.mean(np.sqrt(sx**2 + sy**2)))
    clarity = float(np.std(enh))

    quality = 'High' if clarity > 50 else ('Medium' if clarity > 30 else 'Low')
    rdense  = 'Dense' if density > 20 else ('Moderate' if density > 10 else 'Sparse')

    return quality, rdense, round(clarity, 2), round(density, 2)

# ─────────────────────────────────────────────
# 🚀 MAIN PREDICTION
# ─────────────────────────────────────────────
def run_prediction(img_path: str) -> dict:
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Cannot read image")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Enhance image
    enhanced = _enhance(img_rgb)

    # Normalize (IMPORTANT)
    inp = enhanced.astype(np.float32) / 255.0
    inp = np.expand_dims(inp, axis=0)

    # 🔥 TFLITE INFERENCE
    interpreter.set_tensor(input_details[0]['index'], inp)
    interpreter.invoke()
    preds = interpreter.get_tensor(output_details[0]['index'])[0]

    pred_idx = int(np.argmax(preds))
    confidence = float(np.max(preds))
    pattern = CLASS_NAMES[pred_idx]

    # Additional analysis
    valid, edge_ratio = _valid_fp(img_rgb)
    quality, rdense, clarity, density = _ridge_analysis(img_rgb)

    bg = BG_PROBS[pattern]
    sbg = sorted(bg.items(), key=lambda x: x[1], reverse=True)

    return {
        "pattern": pattern,
        "pattern_info": PATTERN_INFO[pattern],
        "confidence": round(confidence, 4),
        "low_confidence": confidence < CONF_THRESH,
        "pattern_probs": {
            CLASS_NAMES[i]: float(preds[i]) for i in range(len(CLASS_NAMES))
        },
        "blood_group_probs": dict(sbg),
        "top_blood_group": sbg[0][0],
        "top_3": [f"{g} ({p*100:.1f}%)" for g, p in sbg[:3]],
        "image_quality": quality,
        "ridge_density": rdense,
        "clarity_score": clarity,
        "density_score": density,
        "edge_ratio": edge_ratio,
        "valid_fingerprint": valid
    }