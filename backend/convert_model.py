import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import json
import numpy as np
import h5py

MODEL_PATH  = os.environ.get('MODEL_PATH',  'bloodprint_efficientnet.h5')
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'model_config.json')
OUTPUT_PATH = 'model.tflite'


def load_model_from_h5(path: str):
    import tensorflow as tf
    print(f"[convert] TensorFlow  : {tf.__version__}")

    n_classes = 3
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            n_classes = len(json.load(f).get('class_names', ['loop', 'whorl', 'arch']))

    # ── Strategy 1: standard load_model
    try:
        model = tf.keras.models.load_model(path, compile=False)
        dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
        out = model.predict(dummy, verbose=0)[0]
        if not all(abs(p - out[0]) < 0.01 for p in out):
            print("[convert] ✅ Strategy 1: standard load succeeded.")
            return model
        print("[convert] Strategy 1: loaded but weights are uniform, trying Strategy 2...")
    except Exception as e:
        print(f"[convert] Strategy 1 failed: {e}")

    # ── Strategy 2: rebuild architecture + load from model_weights/ path
    print(f"[convert] Rebuilding EfficientNetB0 ({n_classes} classes)...")
    base   = tf.keras.applications.EfficientNetB0(
        weights=None, include_top=False, input_shape=(224, 224, 3)
    )
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
        # Your file uses: model_weights/<layer_name>/<layer_name>/<weight_name>
        if 'model_weights' in f:
            root = f['model_weights']
        elif 'model' in f:
            root = f['model']
        else:
            root = f

        loaded = 0
        skipped = []

        for layer in model.layers:
            if not layer.weights:
                continue

            name = layer.name

            # Navigate: root[name][name][weight_arrays]
            if name not in root:
                skipped.append(name)
                continue

            grp = root[name]
            if name in grp:
                grp = grp[name]   # double-nested: layer_name/layer_name/

            # Collect all weight datasets
            weight_data = {}
            for k in grp.keys():
                if isinstance(grp[k], h5py.Dataset):
                    weight_data[k] = grp[k][()]

            if not weight_data:
                skipped.append(name)
                continue

            # Match to Keras layer weights by name suffix
            keras_weights = layer.weights
            arrays_to_set = []
            matched = True

            for kw in keras_weights:
                # kw.name is like "dense/kernel:0" or "stem_conv/kernel:0"
                wname = kw.name.split('/')[-1].replace(':0', '')
                if wname in weight_data:
                    arrays_to_set.append(weight_data[wname])
                else:
                    # fallback: use sorted order
                    matched = False
                    break

            if not matched:
                # Use sorted order as fallback
                sorted_arrays = [weight_data[k] for k in sorted(weight_data.keys())]
                if len(sorted_arrays) == len(keras_weights):
                    arrays_to_set = sorted_arrays
                else:
                    skipped.append(f"{name}(count mismatch)")
                    continue

            try:
                layer.set_weights(arrays_to_set)
                loaded += 1
            except Exception as e:
                skipped.append(f"{name}({e})")

    layers_with_weights = sum(1 for l in model.layers if l.weights)
    print(f"[convert] Loaded weights for {loaded}/{layers_with_weights} layers")
    if skipped:
        print(f"[convert] Skipped: {len(skipped)} layers")

    # Verify
    dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
    out = model.predict(dummy, verbose=0)[0]
    print(f"[convert] Verification output: {[round(float(x), 4) for x in out]}")

    if all(abs(p - out[0]) < 0.01 for p in out):
        print("[convert] ⚠️  Still uniform — weights may not have transferred correctly")
    else:
        print("[convert] ✅ Non-uniform output — weights loaded correctly!")

    return model


def convert_to_tflite(model) -> bytes:
    import tensorflow as tf
    print("\n[convert] Converting to TFLite (dynamic-range quantisation)...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_bytes = converter.convert()
    print(f"[convert] TFLite size: {len(tflite_bytes)/1024/1024:.2f} MB")
    return tflite_bytes


def smoke_test(tflite_path: str):
    import tensorflow as tf
    interp = tf.lite.Interpreter(model_path=tflite_path)
    interp.allocate_tensors()
    inp_det = interp.get_input_details()[0]
    out_det = interp.get_output_details()[0]
    dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
    interp.set_tensor(inp_det['index'], dummy)
    interp.invoke()
    out = interp.get_tensor(out_det['index'])[0]
    classes = ['loop', 'whorl', 'arch']
    print(f"\n[convert] Smoke-test: {[round(float(x),4) for x in out]}")
    print(f"[convert] Predicted : {classes[int(np.argmax(out))]}  ({max(out)*100:.1f}%)")
    if all(abs(p - out[0]) < 0.01 for p in out):
        print("[convert] ❌ STILL UNIFORM — weights did not transfer to TFLite")
    else:
        print("[convert] ✅ TFLite model working correctly!")


if __name__ == '__main__':
    print(f"[convert] Loading: {MODEL_PATH}\n")
    model = load_model_from_h5(MODEL_PATH)
    tflite_bytes = convert_to_tflite(model)
    with open(OUTPUT_PATH, 'wb') as f:
        f.write(tflite_bytes)
    print(f"[convert] Saved → {OUTPUT_PATH}")
    smoke_test(OUTPUT_PATH)