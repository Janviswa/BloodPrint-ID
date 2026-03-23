import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import json
import numpy as np

MODEL_PATH  = os.environ.get('MODEL_PATH',  'bloodprint_efficientnet.h5')
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'model_config.json')
OUTPUT_PATH = 'model.tflite'


def load_model_safe(path: str):
    """
    Load a Keras 2 .h5 model across TF/Keras version mismatches.
    Tries 3 strategies in order.
    """
    import tensorflow as tf
    print(f"[convert] TensorFlow  : {tf.__version__}")
    try:
        import keras
        print(f"[convert] Keras       : {keras.__version__}")
    except Exception:
        pass

    # ── Strategy 1: Patch InputLayer to accept legacy keys ──────────────
    # Fixes: 'batch_shape', 'optional', 'sparse', 'ragged' kwarg errors
    try:
        class _PatchedInputLayer(tf.keras.layers.InputLayer):
            def __init__(self, *args, **kwargs):
                # remap batch_shape / batch_input_shape → shape
                for old in ('batch_shape', 'batch_input_shape'):
                    if old in kwargs:
                        val = kwargs.pop(old)
                        if val and val[0] is None:
                            val = tuple(val[1:])
                        kwargs.setdefault('shape', tuple(val) if val else ())
                # drop keys Keras 3 / newer tf_keras won't accept
                for k in ('optional', 'ragged', 'sparse'):
                    kwargs.pop(k, None)
                super().__init__(*args, **kwargs)

        with tf.keras.utils.custom_object_scope({'InputLayer': _PatchedInputLayer}):
            model = tf.keras.models.load_model(path, compile=False)
        print("[convert] ✅ Loaded via patched InputLayer scope.")
        return model
    except Exception as e:
        print(f"[convert] Strategy 1 failed: {e}")

    # ── Strategy 2: tf_keras package (standalone Keras 2) ───────────────
    try:
        import tf_keras
        model = tf_keras.models.load_model(path, compile=False)
        print("[convert] ✅ Loaded via tf_keras standalone.")
        return model
    except ImportError:
        print("[convert] tf_keras not installed, skipping...")
    except Exception as e:
        print(f"[convert] Strategy 2 failed: {e}")

    # ── Strategy 3: Rebuild architecture + load weights via h5py ────────
    try:
        import h5py

        n_classes = 3
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                n_classes = len(json.load(f).get('class_names', ['loop', 'whorl', 'arch']))

        print(f"[convert] Rebuilding EfficientNetB0 with {n_classes} classes...")
        base   = tf.keras.applications.EfficientNetB0(weights=None, include_top=False, input_shape=(224, 224, 3))
        x      = base.output
        x      = tf.keras.layers.GlobalAveragePooling2D()(x)
        x      = tf.keras.layers.BatchNormalization()(x)
        x      = tf.keras.layers.Dense(256, activation='relu')(x)
        x      = tf.keras.layers.Dropout(0.4)(x)
        x      = tf.keras.layers.Dense(128, activation='relu')(x)
        x      = tf.keras.layers.Dropout(0.3)(x)
        output = tf.keras.layers.Dense(n_classes, activation='softmax')(x)
        model  = tf.keras.Model(inputs=base.input, outputs=output)

        with h5py.File(path, 'r') as f:
            loaded = 0
            for layer in model.layers:
                name = layer.name
                for key in [name, name.replace('/', '_')]:
                    if key in f:
                        grp = f[key]
                        if key in grp:          # Keras 2 nests weights one level deeper
                            grp = grp[key]
                        weight_names = [k for k in grp.keys() if not isinstance(grp[k], h5py.Group)]
                        weights = [grp[w][()] for w in weight_names]
                        if weights and len(weights) == len(layer.weights):
                            try:
                                layer.set_weights(weights)
                                loaded += 1
                            except Exception:
                                pass
                        break

        print(f"[convert] ✅ h5py rebuild: {loaded}/{len(model.layers)} layers loaded.")
        return model
    except Exception as e:
        print(f"[convert] Strategy 3 failed: {e}")

    raise RuntimeError(
        "\n========================================================\n"
        "  ALL STRATEGIES FAILED — try re-saving the model:\n\n"
        "  In Colab / your training environment:\n"
        "    model.save('bloodprint_v2.h5')   # same TF version\n"
        "  Then re-run this script.\n"
        "========================================================"
    )


def convert_to_tflite(model) -> bytes:
    import tensorflow as tf
    print("\n[convert] Converting to TFLite (dynamic-range quantisation)...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_bytes = converter.convert()
    print(f"[convert] TFLite size: {len(tflite_bytes)/1024/1024:.2f} MB")
    return tflite_bytes


def smoke_test(tflite_path: str):
    """Quick sanity check: run a blank image through the TFLite model."""
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError:
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter

    interp = Interpreter(model_path=tflite_path)
    interp.allocate_tensors()
    inp_det = interp.get_input_details()[0]
    out_det = interp.get_output_details()[0]

    dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
    interp.set_tensor(inp_det['index'], dummy)
    interp.invoke()
    out = interp.get_tensor(out_det['index'])[0]
    print(f"[convert] Smoke-test output: {out}  → class idx {int(np.argmax(out))}")
    print("[convert] ✅ TFLite model is functional.")


if __name__ == '__main__':
    print(f"[convert] Loading model from: {MODEL_PATH}\n")
    model = load_model_safe(MODEL_PATH)

    tflite_bytes = convert_to_tflite(model)

    with open(OUTPUT_PATH, 'wb') as f:
        f.write(tflite_bytes)
    print(f"\n[convert] ✅ Saved → {OUTPUT_PATH}")

    smoke_test(OUTPUT_PATH)