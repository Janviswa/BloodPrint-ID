# -*- coding: utf-8 -*-
"""
train_model.py — BloodPrint ID  (Step 2 of 3)
══════════════════════════════════════════════════════
What this file does:
  1. Reads cluster folders produced by feature_extraction.py
  2. Trains EfficientNetB0 classifier in two phases:
       Phase 1 → head only (base model frozen)
       Phase 2 → fine-tune top 20 EfficientNet layers
  3. Uses EarlyStopping + ReduceLROnPlateau + ModelCheckpoint
  4. Saves the trained model  →  bloodprint_efficientnet.h5
  5. Saves class mapping      →  model_config.json
  6. Plots training curves    →  training_history.png
  7. Prints confusion matrix  →  confusion_matrix.png

⚠️  BEFORE running this file:
  - Open /content/results/cluster_inspection.png
  - Identify which cluster number = loop / whorl / arch
  - Enter the correct order when prompted

Run order:
  ① python feature_extraction.py
  ② python train_model.py             ← YOU ARE HERE
  ③ python prediction.py

Output files produced:
  /content/bloodprint_efficientnet.h5
  /content/model_config.json
  /content/results/training_history.png
  /content/results/confusion_matrix.png
"""

# !pip install tensorflow opencv-python scikit-learn matplotlib seaborn

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf

from tensorflow.keras.applications         import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing.image  import ImageDataGenerator
from sklearn.metrics import confusion_matrix, classification_report

from config import (
    CLUSTERS_DIR, MODEL_SAVE, CONFIG_SAVE, RESULTS_DIR,
    NUM_CLUSTERS, IMG_SIZE, BATCH_SIZE, EPOCHS
)


# ──────────────────────────────────────────────────────────────
# 🔵  TRAINING
# ──────────────────────────────────────────────────────────────
def build_model():
    """
    EfficientNetB0 base + custom classification head.

    Architecture:
      EfficientNetB0 (frozen) → GlobalAveragePool → BN
      → Dense(256, relu) → Dropout(0.4)
      → Dense(128, relu) → Dropout(0.3)
      → Dense(3, softmax)
    """
    base = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        input_shape=(*IMG_SIZE, 3)
    )
    base.trainable = False  # frozen in Phase 1

    x      = base.output
    x      = tf.keras.layers.GlobalAveragePooling2D()(x)
    x      = tf.keras.layers.BatchNormalization()(x)
    x      = tf.keras.layers.Dense(256, activation='relu')(x)
    x      = tf.keras.layers.Dropout(0.4)(x)
    x      = tf.keras.layers.Dense(128, activation='relu')(x)
    x      = tf.keras.layers.Dropout(0.3)(x)
    output = tf.keras.layers.Dense(NUM_CLUSTERS, activation='softmax')(x)

    return tf.keras.Model(inputs=base.input, outputs=output), base


def get_data_generators():
    """
    ImageDataGenerator using EfficientNet's preprocess_input.
    (NOT rescale=1/255 — that was the original bug.)
    Augmentation: rotation, flip, zoom, small shifts.
    """
    datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        validation_split=0.2,
        rotation_range=15,
        horizontal_flip=True,
        zoom_range=0.1,
        width_shift_range=0.05,
        height_shift_range=0.05,
    )

    train_gen = datagen.flow_from_directory(
        CLUSTERS_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True,
    )

    val_gen = datagen.flow_from_directory(
        CLUSTERS_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False,
    )

    return train_gen, val_gen


def get_callbacks():
    return [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=4,
            restore_best_weights=True, verbose=1),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', patience=2,
            factor=0.5, min_lr=1e-7, verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            MODEL_SAVE, monitor='val_accuracy',
            save_best_only=True, verbose=1),
    ]


def train_model(class_names):
    """Full two-phase training pipeline."""

    train_gen, val_gen = get_data_generators()
    model, base        = build_model()
    callbacks          = get_callbacks()

    print(f"\n📊 Keras class index mapping: {train_gen.class_indices}")
    print(f"   Your class_names:          {class_names}")
    print(f"   Training samples  : {train_gen.samples}")
    print(f"   Validation samples: {val_gen.samples}")
    print(f"   Model parameters  : {model.count_params():,}")

    # ── Phase 1: train head only
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )
    print("\n" + "─"*55)
    print("  🚀  Phase 1 — Training classifier head  (base frozen)")
    print("─"*55)
    h1 = model.fit(
        train_gen, validation_data=val_gen,
        epochs=EPOCHS, callbacks=callbacks,
    )

    # ── Phase 2: fine-tune top 20 EfficientNet layers
    for layer in base.layers[-20:]:
        layer.trainable = True

    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-5),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )
    print("\n" + "─"*55)
    print("  🚀  Phase 2 — Fine-tuning top 20 EfficientNet layers")
    print("─"*55)
    h2 = model.fit(
        train_gen, validation_data=val_gen,
        epochs=5, callbacks=callbacks,
    )

    # Merge history for plotting
    full_history = {}
    for key in h1.history:
        full_history[key] = h1.history[key] + h2.history.get(key, [])

    print(f"\n✅ Training complete!  Best model saved → {MODEL_SAVE}")
    return model, val_gen, full_history


# ──────────────────────────────────────────────────────────────
# 📊  EVALUATION PLOTS
# ──────────────────────────────────────────────────────────────
def plot_training_history(history):
    """
    Plot accuracy and loss curves side-by-side.
    A widening gap between train and val lines = overfitting.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4))
    fig.patch.set_facecolor('#0d0d1a')

    epochs = range(1, len(history['accuracy']) + 1)

    for ax in (ax1, ax2):
        ax.set_facecolor('#1a1a2e')
        ax.tick_params(colors='white')
        ax.spines[:].set_color('#444')

    ax1.plot(epochs, history['accuracy'],
             color='#4cc9f0', lw=2, label='Train Accuracy')
    ax1.plot(epochs, history['val_accuracy'],
             color='#f72585', lw=2, ls='--', label='Val Accuracy')
    ax1.set_title('Accuracy per Epoch', color='white', fontsize=12, pad=8)
    ax1.set_xlabel('Epoch', color='white')
    ax1.set_ylabel('Accuracy', color='white')
    ax1.legend(facecolor='#222', labelcolor='white')

    ax2.plot(epochs, history['loss'],
             color='#4cc9f0', lw=2, label='Train Loss')
    ax2.plot(epochs, history['val_loss'],
             color='#f72585', lw=2, ls='--', label='Val Loss')
    ax2.set_title('Loss per Epoch', color='white', fontsize=12, pad=8)
    ax2.set_xlabel('Epoch', color='white')
    ax2.set_ylabel('Loss', color='white')
    ax2.legend(facecolor='#222', labelcolor='white')

    plt.tight_layout()
    out = f"{RESULTS_DIR}/training_history.png"
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#0d0d1a')
    plt.show()
    print(f"📊 Training history saved → {out}")


def plot_confusion_matrix(model, val_gen, class_names):
    """
    Run model on entire validation set, plot confusion matrix,
    and print per-class precision / recall / F1.
    """
    print("\n🔄 Running evaluation on validation set...")

    y_true, y_pred = [], []
    val_gen.reset()
    steps = int(np.ceil(val_gen.samples / val_gen.batch_size))

    for _ in range(steps):
        bx, by = next(val_gen)
        preds  = model.predict(bx, verbose=0)
        y_true.extend(np.argmax(by,    axis=1))
        y_pred.extend(np.argmax(preds, axis=1))

    y_true = y_true[:val_gen.samples]
    y_pred = y_pred[:val_gen.samples]

    # Text report
    print("\n📋 Classification Report:")
    print(classification_report(y_true, y_pred, target_names=class_names))

    # Heatmap
    cm  = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor('#0d0d1a')
    ax.set_facecolor('#1a1a2e')

    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=class_names, yticklabels=class_names,
        ax=ax, linewidths=0.5, linecolor='#333',
        annot_kws={"size": 13, "color": "white"}
    )
    ax.set_title('Confusion Matrix (Validation Set)',
                 color='white', fontsize=12, pad=10)
    ax.set_xlabel('Predicted', color='white')
    ax.set_ylabel('Actual',    color='white')
    ax.tick_params(colors='white')

    plt.tight_layout()
    out = f"{RESULTS_DIR}/confusion_matrix.png"
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#0d0d1a')
    plt.show()
    print(f"📊 Confusion matrix saved → {out}")


def save_config(class_names, train_gen, val_gen):
    """Save class mapping and training metadata to JSON."""
    config = {
        "class_names"      : class_names,
        "num_clusters"     : NUM_CLUSTERS,
        "img_size"         : list(IMG_SIZE),
        "base_model"       : "EfficientNetB0",
        "training_images"  : train_gen.samples,
        "validation_images": val_gen.samples,
    }
    with open(CONFIG_SAVE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"💾 Config saved → {CONFIG_SAVE}")


# ──────────────────────────────────────────────────────────────
# ▶  MAIN
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🩸  BloodPrint ID — Step 2: Train Model")
    print("="*60)

    # ── Verify clusters exist
    if not os.path.exists(CLUSTERS_DIR):
        print("❌ Cluster folder not found!")
        print("   Run feature_extraction.py first.")
        exit(1)

    # ── Ask user to confirm cluster → pattern mapping
    print("""
  ⚠️  IMPORTANT: Open cluster_inspection.png first!
  KMeans labels clusters as 0 / 1 / 2 randomly.
  You must tell this script which cluster is which pattern.

  Default: cluster_0=loop, cluster_1=whorl, cluster_2=arch
  """)

    custom = input(
        "  Enter correct order as: loop,whorl,arch  "
        "(or press Enter for default): "
    ).strip()

    class_names = (
        [c.strip().lower() for c in custom.split(",")]
        if custom else ['loop', 'whorl', 'arch']
    )
    print(f"\n  ✅ Mapping → cluster_0={class_names[0]}, "
          f"cluster_1={class_names[1]}, cluster_2={class_names[2]}")

    # ── Train
    model, val_gen, history = train_model(class_names)

    # ── Evaluate
    plot_training_history(history)
    plot_confusion_matrix(model, val_gen, class_names)

    # ── Save config (needed by prediction.py)
    train_gen, val_gen = get_data_generators()
    save_config(class_names, train_gen, val_gen)

    print("\n" + "="*60)
    print("  ✅  Training complete!")
    print(f"  Model saved → {MODEL_SAVE}")
    print(f"  Config saved → {CONFIG_SAVE}")
    print("  👉  Next: run  →  python prediction.py")
    print("="*60)
