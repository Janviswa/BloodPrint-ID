import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import tensorflow as tf

# 🔥 EXACT architecture from your training code
def build_model():
    base = tf.keras.applications.EfficientNetB0(
        weights=None,                # IMPORTANT
        include_top=False,
        input_shape=(224, 224, 3)
    )

    x = base.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    x = tf.keras.layers.Dense(128, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    output = tf.keras.layers.Dense(3, activation='softmax')(x)

    model = tf.keras.Model(inputs=base.input, outputs=output)
    return model

print("🔧 Rebuilding model...")
model = build_model()

print("📥 Loading weights...")
model.load_weights("bloodprint_efficientnet.h5")

print("✅ Model ready!")

# 🔥 Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

with open("model.tflite", "wb") as f:
    f.write(tflite_model)

print("🎉 SUCCESS — model.tflite created!")