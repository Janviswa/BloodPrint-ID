# predictor.py — TFLite inference with same preprocessing as training
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import json
import numpy as np

MODEL_PATH  = os.environ.get('MODEL_PATH',  'model.tflite')
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'model_config.json')
IMG_SIZE    = (224, 224)
CONF_THRESH = 0.55

# ── Static data ───────────────────────────────────────────────
PATTERN_INFO = {
    'loop': {
        'full_name':       'Loop Pattern',
        'prevalence':      '~65% of population',
        'description':     'Ridge lines enter from one side of the finger, curve around a central core point, and exit from the same side. Sub-types: Ulnar Loop (opens toward little finger) and Radial Loop (opens toward thumb).',
        'characteristics': [
            'Exactly one delta point visible',
            'Ridges open on one side only',
            'Core forms a rounded loop shape',
            'Ridge count measured between core and delta',
            'Ulnar loops are far more common than radial loops',
        ],
        'ridge_count': 'Typically 5-15 ridges between delta and core',
    },
    'whorl': {
        'full_name':       'Whorl Pattern',
        'prevalence':      '~30% of population',
        'description':     'Ridges form complete circular or spiral circuits around a central core. Sub-types: Plain Whorl, Central Pocket Loop, Double Loop Whorl, and Accidental Whorl.',
        'characteristics': [
            'Two delta points present (left and right)',
            'At least one ridge completes a full 360 degree circuit',
            'Core is centrally positioned',
            'Can appear as concentric circles or tight spiral',
            'Double loop whorl contains two separate cores',
        ],
        'ridge_count': 'Inner tracing method used (inner / meeting / outer)',
    },
    'arch': {
        'full_name':       'Arch Pattern',
        'prevalence':      '~5% of population',
        'description':     'The simplest fingerprint pattern. Ridges enter from one side, rise gently in the center, and exit on the opposite side. No delta or core present. Sub-types: Plain Arch and Tented Arch.',
        'characteristics': [
            'No delta points whatsoever',
            'No core present',
            'Ridges flow smoothly side-to-side',
            'Center ridges rise to a gentle or sharp peak',
            'Tented arch has an upright spike at center',
        ],
        'ridge_count': 'No ridge count possible (no delta or core)',
    },
}

_RAW = {
    'loop':  {'O+':0.28,'O-':0.08,'A+':0.22,'A-':0.06,'B+':0.16,'B-':0.05,'AB+':0.10,'AB-':0.05},
    'whorl': {'O+':0.18,'O-':0.05,'A+':0.15,'A-':0.04,'B+':0.28,'B-':0.08,'AB+':0.14,'AB-':0.08},
    'arch':  {'O+':0.18,'O-':0.06,'A+':0.22,'A-':0.08,'B+':0.12,'B-':0.04,'AB+':0.20,'AB-':0.10},
}

def _norm(d):
    t = sum(d.values())
    return {k: round(v / t, 6) for k, v in d.items()}

BG_PROBS = {k: _norm(v) for k, v in _RAW.items()}

# ── Lazy TFLite interpreter + class names ─────────────────────
_interpreter  = None
_input_det    = None
_output_det   = None
_class_names  = ['loop', 'whorl', 'arch']


def _get_interpreter():
    global _interpreter, _input_det, _output_det, _class_names

    if _interpreter is not None:
        return _interpreter, _input_det, _output_det, _class_names

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"TFLite model not found at: {MODEL_PATH}\n"
            "Run convert_model.py first to generate model.tflite."
        )

    # tflite_runtime is lighter on RAM (preferred on Render)
    # falls back to full TF if tflite_runtime is not installed
    try:
        from tflite_runtime.interpreter import Interpreter
        print("[predictor] Using tflite_runtime")
    except ImportError:
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter
        print("[predictor] Using tensorflow.lite (tflite_runtime not found)")

    _interpreter = Interpreter(model_path=MODEL_PATH)
    _interpreter.allocate_tensors()
    _input_det  = _interpreter.get_input_details()[0]
    _output_det = _interpreter.get_output_details()[0]

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            _class_names = json.load(f)['class_names']

    print(f"[predictor] TFLite model loaded. Classes: {_class_names}")
    print(f"[predictor] Input  dtype : {_input_det['dtype']}")
    print(f"[predictor] Input  shape : {_input_det['shape']}")
    print(f"[predictor] Output shape : {_output_det['shape']}")

    return _interpreter, _input_det, _output_det, _class_names


# ── Image helpers ─────────────────────────────────────────────
def _clahe(gray):
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

def _enhance(img_rgb):
    resized  = cv2.resize(img_rgb, IMG_SIZE)
    enhanced = np.stack([_clahe(resized[:, :, c]) for c in range(3)], axis=-1)
    return enhanced

def _valid_fp(img_rgb):
    gray  = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    ratio = float(np.sum(edges > 0) / edges.size)
    return ratio >= 0.05, round(ratio, 4)

def _ridge_analysis(img_rgb):
    gray    = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    small   = cv2.resize(gray, (128, 128))
    enh     = _clahe(small)
    sx      = cv2.Sobel(enh, cv2.CV_64F, 1, 0, ksize=3)
    sy      = cv2.Sobel(enh, cv2.CV_64F, 0, 1, ksize=3)
    density = float(np.mean(np.sqrt(sx**2 + sy**2)))
    clarity = float(np.std(enh))
    quality = 'High'     if clarity > 50 else ('Medium' if clarity > 30 else 'Low')
    rdense  = 'Dense'    if density > 20 else ('Moderate' if density > 10 else 'Sparse')
    return quality, rdense, round(clarity, 2), round(density, 2)


def _efficientnet_preprocess(img_rgb_uint8: np.ndarray) -> np.ndarray:
    """
    Mirror of tensorflow.keras.applications.efficientnet.preprocess_input.
    Scales [0, 255] → [-1, 1].
    Done manually so we avoid importing full TF on the Render instance.
    """
    img = img_rgb_uint8.astype(np.float32)
    img /= 127.5
    img -= 1.0
    return img


# ── Main predict ──────────────────────────────────────────────
def run_prediction(img_path: str) -> dict:
    img_bgr = cv2.imread(img_path)
    if img_bgr is None:
        raise ValueError('Cannot read image file.')

    img_rgb  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    enhanced = _enhance(img_rgb)                          # CLAHE + resize to 224×224

    inp = _efficientnet_preprocess(enhanced)              # [-1, 1] float32
    inp = np.expand_dims(inp, axis=0)                     # (1, 224, 224, 3)

    interp, inp_det, out_det, class_names = _get_interpreter()

    # Handle quantised (uint8/int8) models transparently
    if inp_det['dtype'] == np.uint8:
        scale, zero_point = inp_det['quantization']
        inp = np.clip(np.round(inp / scale + zero_point), 0, 255).astype(np.uint8)
    elif inp_det['dtype'] == np.int8:
        scale, zero_point = inp_det['quantization']
        inp = np.clip(np.round(inp / scale + zero_point), -128, 127).astype(np.int8)

    interp.set_tensor(inp_det['index'], inp)
    interp.invoke()
    raw_out = interp.get_tensor(out_det['index'])[0]

    # Dequantise output if needed
    if out_det['dtype'] in (np.uint8, np.int8):
        scale, zero_point = out_det['quantization']
        preds = (raw_out.astype(np.float32) - zero_point) * scale
    else:
        preds = raw_out.astype(np.float32)

    print(f"[predictor] Raw output ({class_names}): {preds}")

    pred_idx   = int(np.argmax(preds))
    confidence = float(np.max(preds))
    pattern    = class_names[pred_idx]

    pattern_probs = {
        class_names[i]: round(float(preds[i]), 4)
        for i in range(len(class_names))
    }

    valid, edge_ratio                    = _valid_fp(img_rgb)
    quality, rdense, clarity, density   = _ridge_analysis(img_rgb)
    bg  = BG_PROBS[pattern]
    sbg = sorted(bg.items(), key=lambda x: x[1], reverse=True)

    return {
        'pattern':           pattern,
        'pattern_info':      PATTERN_INFO[pattern],
        'confidence':        round(confidence, 4),
        'low_confidence':    confidence < CONF_THRESH,
        'pattern_probs':     pattern_probs,
        'blood_group_probs': dict(sbg),
        'top_blood_group':   sbg[0][0],
        'top_3':             [f"{g} ({p*100:.1f}%)" for g, p in sbg[:3]],
        'image_quality':     quality,
        'ridge_density':     rdense,
        'clarity_score':     clarity,
        'density_score':     density,
        'edge_ratio':        edge_ratio,
        'valid_fingerprint': valid,
    }