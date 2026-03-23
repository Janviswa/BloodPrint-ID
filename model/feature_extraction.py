# -*- coding: utf-8 -*-
"""
feature_extraction.py — BloodPrint ID  (Step 1 of 3)
══════════════════════════════════════════════════════
What this file does:
  1. Loads every fingerprint image from the dataset
  2. Enhances each image with CLAHE (fixes uneven lighting)
  3. Extracts deep features using EfficientNetB0 (pretrained)
  4. Saves features to disk  →  crash-safe, no re-extraction needed
  5. Clusters images into 3 groups (loop / whorl / arch) via KMeans
  6. Copies images into cluster_0 / cluster_1 / cluster_2 folders
  7. Shows a visual grid so you can name each cluster correctly

Run order:
  ① python feature_extraction.py      ← YOU ARE HERE
  ② python train_model.py
  ③ python prediction.py

Output files produced:
  /content/features.npy
  /content/image_names.npy
  /content/clusters/cluster_0/  cluster_1/  cluster_2/
  /content/results/cluster_inspection.png
"""

# !pip install tensorflow opencv-python scikit-learn matplotlib

import os
import cv2
import shutil
import numpy as np
import matplotlib.pyplot as plt

from tensorflow.keras.applications         import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from sklearn.cluster   import KMeans
from sklearn.preprocessing import normalize

from config import (
    DATASET_PATH, CLUSTERS_DIR, FEATURES_PATH, NAMES_PATH,
    RESULTS_DIR, NUM_CLUSTERS, IMG_SIZE, BATCH_SIZE, VALID_EXTENSIONS
)


# ──────────────────────────────────────────────────────────────
# 🛠️  HELPER
# ──────────────────────────────────────────────────────────────
def enhance_fingerprint(gray_img):
    """
    CLAHE — Contrast Limited Adaptive Histogram Equalization.
    Corrects uneven brightness on low-quality scanner images
    before feeding into the neural network.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray_img)


def load_and_preprocess(img_path):
    """
    Read image → BGR→RGB → resize → CLAHE per channel
    → EfficientNet preprocess_input.
    Returns None if file is unreadable.
    """
    img = cv2.imread(img_path)
    if img is None:
        return None

    img_rgb  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_rgb  = cv2.resize(img_rgb, IMG_SIZE)

    # Apply CLAHE to each channel individually
    enhanced = np.stack(
        [enhance_fingerprint(img_rgb[:, :, c]) for c in range(3)],
        axis=-1
    )
    return preprocess_input(enhanced.astype(np.float32))


# ──────────────────────────────────────────────────────────────
# 🔵  STEP 1A — FEATURE EXTRACTION
# ──────────────────────────────────────────────────────────────
def extract_features():
    """
    Extract 1280-dim feature vectors from every image using
    EfficientNetB0 (ImageNet weights, no top layer).

    Results are saved to disk so if Colab crashes you can
    reload instantly without repeating the ~2hr extraction.
    """

    # ── Load from cache if already done
    if os.path.exists(FEATURES_PATH) and os.path.exists(NAMES_PATH):
        print("💾 Cached features found — loading from disk...")
        features    = np.load(FEATURES_PATH)
        image_names = np.load(NAMES_PATH).tolist()
        print(f"✅ Loaded {len(image_names)} vectors  |  shape: {features.shape}")
        return features, image_names

    # ── Build feature extractor
    print("🧠 Loading EfficientNetB0 feature extractor...")
    feat_model = EfficientNetB0(weights='imagenet', include_top=False, pooling='avg')

    image_files = sorted([
        f for f in os.listdir(DATASET_PATH)
        if f.lower().endswith(VALID_EXTENSIONS)
    ])
    total = len(image_files)
    print(f"📂 Dataset: {total} images found in {DATASET_PATH}")
    print("🚀 Starting feature extraction...\n")

    features, image_names     = [], []
    batch_imgs, batch_names   = [], []

    for i, img_name in enumerate(image_files):
        img_path    = os.path.join(DATASET_PATH, img_name)
        preprocessed = load_and_preprocess(img_path)

        if preprocessed is None:
            print(f"  ⚠️  Skipping unreadable file: {img_name}")
            continue

        batch_imgs.append(preprocessed)
        batch_names.append(img_name)

        # Process when batch is full or last image reached
        if len(batch_imgs) == BATCH_SIZE or i == total - 1:
            batch_feats = feat_model.predict(np.array(batch_imgs), verbose=0)
            features.extend(batch_feats.tolist())
            image_names.extend(batch_names)
            batch_imgs, batch_names = [], []

            done = min(i + 1, total)
            pct  = done / total * 100
            bar  = "█" * int(pct / 2)
            print(f"  [{bar:<50}] {done}/{total}  ({pct:.1f}%)", end='\r')

    features = np.array(features)
    print(f"\n\n✅ Extraction complete!  Shape: {features.shape}")

    # ── Save to disk
    np.save(FEATURES_PATH, features)
    np.save(NAMES_PATH, np.array(image_names))
    print(f"💾 Saved → {FEATURES_PATH}")
    print(f"💾 Saved → {NAMES_PATH}")

    return features, image_names


# ──────────────────────────────────────────────────────────────
# 🔵  STEP 1B — CLUSTERING
# ──────────────────────────────────────────────────────────────
def cluster_images(features, image_names):
    """
    KMeans clustering on L2-normalized features.
    n_init=10 for stable results across runs.
    """
    print("\n🔄 Clustering into", NUM_CLUSTERS, "groups...")
    feats_norm = normalize(features)
    kmeans     = KMeans(n_clusters=NUM_CLUSTERS, random_state=42, n_init=10)
    labels     = kmeans.fit_predict(feats_norm)

    print("✅ Clustering complete!")
    for i in range(NUM_CLUSTERS):
        count = int(np.sum(labels == i))
        print(f"   Cluster {i} → {count} images  ({count/len(labels)*100:.1f}%)")

    return labels, kmeans


def save_clusters(labels, image_names):
    """Copy each image into its cluster folder."""
    print("\n📂 Saving images to cluster folders...")

    for i in range(NUM_CLUSTERS):
        os.makedirs(f"{CLUSTERS_DIR}/cluster_{i}", exist_ok=True)

    skipped = 0
    for idx, label in enumerate(labels):
        src = os.path.join(DATASET_PATH, image_names[idx])
        dst = f"{CLUSTERS_DIR}/cluster_{label}/{image_names[idx]}"
        if os.path.exists(src):
            shutil.copy(src, dst)
        else:
            skipped += 1

    print(f"✅ Done!  (skipped {skipped} missing files)")
    print(f"   Folders → {CLUSTERS_DIR}/cluster_0 / cluster_1 / cluster_2")


# ──────────────────────────────────────────────────────────────
# 🔵  STEP 1C — CLUSTER INSPECTION
# ──────────────────────────────────────────────────────────────
def inspect_clusters(n_samples=6):
    """
    Display a grid of sample images from each cluster.

    ⚠️  KMeans assigns numbers (0, 1, 2) randomly — the cluster
    numbers do NOT automatically mean loop/whorl/arch.
    You MUST look at this grid and decide which cluster is which
    before running train_model.py.
    """
    print("\n" + "="*60)
    print("  👁️  CLUSTER INSPECTION")
    print("  Look at the grid → decide which cluster = loop/whorl/arch")
    print("="*60)

    fig, axes = plt.subplots(
        NUM_CLUSTERS, n_samples,
        figsize=(n_samples * 2.5, NUM_CLUSTERS * 2.8)
    )
    fig.patch.set_facecolor('#0d0d1a')
    fig.suptitle(
        "Cluster Samples  —  Inspect then assign Loop / Whorl / Arch labels",
        color='white', fontsize=12, y=1.01
    )

    for cluster_id in range(NUM_CLUSTERS):
        folder  = f"{CLUSTERS_DIR}/cluster_{cluster_id}"
        samples = sorted(os.listdir(folder))[:n_samples]

        for j in range(n_samples):
            ax = axes[cluster_id][j]
            ax.set_facecolor('#1a1a2e')
            ax.axis('off')

            if j < len(samples):
                img = cv2.imread(os.path.join(folder, samples[j]))
                if img is not None:
                    ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cmap='gray')

            if j == 0:
                ax.set_title(
                    f"Cluster {cluster_id}",
                    color='white', fontsize=11, pad=6, loc='left'
                )

    plt.tight_layout()
    out = f"{RESULTS_DIR}/cluster_inspection.png"
    plt.savefig(out, dpi=120, bbox_inches='tight', facecolor='#0d0d1a')
    plt.show()
    print(f"\n📸 Saved → {out}")
    print("\n⚠️  NOW open model_config.json and set class_names in the correct order.")
    print("   Example: if cluster_0=whorl, cluster_1=loop, cluster_2=arch")
    print('   Set:  "class_names": ["whorl", "loop", "arch"]')


# ──────────────────────────────────────────────────────────────
# ▶  MAIN
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🩸  BloodPrint ID — Step 1: Feature Extraction")
    print("="*60)

    # Step 1A — extract (or load from cache)
    features, image_names = extract_features()

    # Step 1B — cluster
    labels, _ = cluster_images(features, image_names)

    # Step 1C — save to folders
    save_clusters(labels, image_names)

    # Step 1D — visual inspection
    inspect_clusters(n_samples=6)

    print("\n" + "="*60)
    print("  ✅  Feature extraction complete!")
    print("  👉  Next: open cluster_inspection.png, identify each cluster,")
    print("      then run  →  python train_model.py")
    print("="*60)
