# predictor.py — same preprocessing as training
# Compatible with TF 2.x (Keras 2) and TF 2.16+ (Keras 3)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# Force Keras 2 compatibility BEFORE importing tensorflow
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import cv2, json
import numpy as np
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

tf.config.set_visible_devices([], 'GPU')  # disable GPU

MODEL_PATH  = os.environ.get('MODEL_PATH',  'bloodprint_efficientnet.h5')
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

# ── Lazy model + class names ──────────────────────────────────
_model       = None
_class_names = ['loop', 'whorl', 'arch']


def _load_model_compat(path: str):
    """
    Try every known strategy to load a Keras 2 .h5 model,
    even when running on TF 2.16+ (Keras 3).
    """
    import tensorflow as tf

    tf_version = tf.__version__
    print(f"[predictor] TensorFlow {tf_version}")

    # ── Try to detect Keras version
    try:
        import keras
        keras_version = keras.__version__
        print(f"[predictor] Keras {keras_version}")
    except Exception:
        keras_version = 'unknown'

    # ── Strategy A: tf_keras (standalone Keras 2 package)
    #    Install with:  pip install tf_keras
    try:
        import tf_keras
        model = tf_keras.models.load_model(path, compile=False)
        print("[predictor] Loaded via tf_keras (Keras 2 standalone).")
        return model
    except ImportError:
        print("[predictor] tf_keras not installed, trying next strategy...")
    except Exception as e:
        print(f"[predictor] tf_keras load failed: {e}")

    # ── Strategy B: standard keras load (works on TF <= 2.15)
    try:
        from tensorflow.keras.models import load_model
        model = load_model(path, compile=False)
        print("[predictor] Loaded via tensorflow.keras.")
        return model
    except Exception as e:
        print(f"[predictor] tensorflow.keras load failed: {e}")

    # ── Strategy C: patch InputLayer config keys at load time
    #    Fixes 'batch_shape', 'optional', 'shape' kwarg mismatches
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model

        class _PatchedInputLayer(tf.keras.layers.InputLayer):
            """Accept any unknown kwargs silently for cross-version compat."""
            def __init__(self, *args, **kwargs):
                # remap legacy keys
                for old, new in [('batch_shape', 'shape'), ('batch_input_shape', 'shape')]:
                    if old in kwargs:
                        val = kwargs.pop(old)
                        if val and val[0] is None:
                            val = tuple(val[1:])
                        else:
                            val = tuple(val) if val else ()
                        kwargs.setdefault('shape', val)
                # drop unknown kwargs that Keras 3 doesn't accept
                for k in ['optional', 'ragged', 'sparse']:
                    kwargs.pop(k, None)
                super().__init__(*args, **kwargs)

        with tf.keras.utils.custom_object_scope({'InputLayer': _PatchedInputLayer}):
            model = load_model(path, compile=False)
        print("[predictor] Loaded via patched InputLayer scope.")
        return model
    except Exception as e:
        print(f"[predictor] Patched scope failed: {e}")

    # ── Strategy D: h5py direct weight extraction + rebuild architecture
    try:
        import h5py
        import tensorflow as tf
        from tensorflow.keras.applications import EfficientNetB0

        print("[predictor] Attempting h5py weight extraction + architecture rebuild...")

        n_classes = 3
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                n_classes = len(json.load(f).get('class_names', ['loop','whorl','arch']))

        # Build identical architecture
        base   = EfficientNetB0(weights=None, include_top=False, input_shape=(224, 224, 3))
        x      = base.output
        x      = tf.keras.layers.GlobalAveragePooling2D()(x)
        x      = tf.keras.layers.BatchNormalization()(x)
        x      = tf.keras.layers.Dense(256, activation='relu')(x)
        x      = tf.keras.layers.Dropout(0.4)(x)
        x      = tf.keras.layers.Dense(128, activation='relu')(x)
        x      = tf.keras.layers.Dropout(0.3)(x)
        output = tf.keras.layers.Dense(n_classes, activation='softmax')(x)
        model  = tf.keras.Model(inputs=base.input, outputs=output)

        # Extract and assign weights by layer name from h5 file
        with h5py.File(path, 'r') as f:
            def _load_layer(layer, f):
                layer_name = layer.name
                # Try both h5 storage formats
                for key in [layer_name, layer_name.replace('/', '_')]:
                    if key in f:
                        grp = f[key]
                        # Keras 2 stores weights under layer_name/layer_name
                        if key in grp:
                            grp = grp[key]
                        weights = [grp[wn][()] for wn in grp.keys() if not isinstance(grp[wn], h5py.Group)]
                        if weights and len(weights) == len(layer.weights):
                            try:
                                layer.set_weights(weights)
                                return True
                            except Exception:
                                pass
                return False

            loaded = 0
            for layer in model.layers:
                if _load_layer(layer, f):
                    loaded += 1

        print(f"[predictor] h5py rebuild: loaded weights for {loaded}/{len(model.layers)} layers.")
        return model
    except Exception as e:
        print(f"[predictor] h5py rebuild failed: {e}")

    raise RuntimeError(
        "\n\n"
        "========================================================\n"
        "  MODEL LOADING FAILED — VERSION MISMATCH\n"
        "========================================================\n"
        f"  Your model was saved with a different Keras version.\n"
        f"  TF version: {tf_version}  |  Keras: {keras_version}\n\n"
        "  QUICKEST FIX — run in your venv:\n"
        "    pip install tf_keras\n\n"
        "  OR re-save in Colab with matching version:\n"
        "    !pip install tensorflow==2.15.0\n"
        "    model.save('/content/bloodprint_v2.h5')\n"
        "    files.download('/content/bloodprint_v2.h5')\n"
        "========================================================"
    )


def _get_model():
    global _model, _class_names
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at: {MODEL_PATH}\n"
                f"Place bloodprint_efficientnet.h5 inside the backend/ folder."
            )
        _model = _load_model_compat(MODEL_PATH)
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                _class_names = json.load(f)['class_names']
        print(f"[predictor] Class names: {_class_names}")
    return _model, _class_names


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


# ── Main predict ──────────────────────────────────────────────
def run_prediction(img_path: str) -> dict:
    from tensorflow.keras.applications.efficientnet import preprocess_input

    img = cv2.imread(img_path)
    if img is None:
        raise ValueError('Cannot read image file.')

    img_rgb  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    enhanced = _enhance(img_rgb)
    inp      = preprocess_input(enhanced.astype(np.float32))
    inp      = np.expand_dims(inp, axis=0)

    model, class_names = _get_model()
    preds      = model.predict(inp, verbose=0)[0]
    pred_idx   = int(np.argmax(preds))
    confidence = float(np.max(preds))
    pattern    = class_names[pred_idx]

    pattern_probs = {
        class_names[i]: round(float(preds[i]), 4)
        for i in range(len(class_names))
    }
    valid, edge_ratio            = _valid_fp(img_rgb)
    quality, rdense, clarity, density = _ridge_analysis(img_rgb)
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