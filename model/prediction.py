# -*- coding: utf-8 -*-
"""
prediction.py — BloodPrint ID  (Step 3 of 3)
══════════════════════════════════════════════════════
What this file does:
  1. Loads the trained model  (bloodprint_efficientnet.h5)
  2. Loads the class mapping  (model_config.json)
  3. Validates the input image is likely a fingerprint
  4. Enhances image quality with CLAHE
  5. Predicts fingerprint pattern  (loop / whorl / arch)
  6. Looks up blood group statistical likelihoods
  7. Prints a detailed full-width analysis report
  8. Saves a 3-panel result chart  →  bloodprint_result.png
  9. Loops so you can test multiple images in one session

Run order:
  ① python feature_extraction.py
  ② python train_model.py
  ③ python prediction.py              ← YOU ARE HERE

Output files produced:
  /content/results/bloodprint_result.png   (per prediction)
"""

# !pip install tensorflow opencv-python matplotlib

import os
import json
import cv2
import numpy as np
import matplotlib.pyplot as plt

from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input

from config import (
    MODEL_SAVE, CONFIG_SAVE, RESULTS_DIR,
    IMG_SIZE, CONF_THRESHOLD,
    PATTERN_INFO, BLOOD_GROUP_PROBS
)


# ──────────────────────────────────────────────────────────────
# 🛠️  IMAGE UTILITIES
# ──────────────────────────────────────────────────────────────
def enhance_fingerprint(gray_img):
    """
    CLAHE enhancement — corrects uneven lighting on scanned images.
    Must match the same enhancement used during training.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray_img)


def is_valid_fingerprint(img_rgb):
    """
    Quick validity check using Canny edge density.
    Real fingerprints have a high density of fine ridge edges.
    Returns: (is_valid: bool, edge_ratio: float)
    """
    gray       = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    edges      = cv2.Canny(gray, 50, 150)
    edge_ratio = float(np.sum(edges > 0) / edges.size)
    return edge_ratio >= 0.05, edge_ratio


def analyze_ridges(img_rgb):
    """
    Estimate image quality and ridge density using Sobel gradients.
    Returns: quality label, density label, clarity score, density score.
    """
    gray      = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    small     = cv2.resize(gray, (128, 128))
    enhanced  = enhance_fingerprint(small)

    sobelx    = cv2.Sobel(enhanced, cv2.CV_64F, 1, 0, ksize=3)
    sobely    = cv2.Sobel(enhanced, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)

    density   = float(np.mean(magnitude))
    clarity   = float(np.std(enhanced))

    quality       = "High"     if clarity > 50 else ("Medium" if clarity > 30 else "Low")
    ridge_density = "Dense"    if density > 20 else ("Moderate" if density > 10 else "Sparse")

    return quality, ridge_density, clarity, density


def preprocess_for_model(img_path):
    """
    Load → BGR→RGB → resize → CLAHE per channel
    → EfficientNet preprocess_input → add batch dimension.
    Returns: (raw_rgb, model_ready_batch)
    """
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {img_path}")

    img_rgb  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resized  = cv2.resize(img_rgb, IMG_SIZE)

    enhanced = np.stack(
        [enhance_fingerprint(resized[:, :, c]) for c in range(3)],
        axis=-1
    )
    model_input = preprocess_input(enhanced.astype(np.float32))
    return img_rgb, np.expand_dims(model_input, axis=0)


# ──────────────────────────────────────────────────────────────
# 🔵  PREDICTION + REPORT
# ──────────────────────────────────────────────────────────────
def predict_and_report(img_path, model, class_names):
    """
    Full pipeline for one image:
      validate → enhance → predict → blood group lookup
      → print report → save chart
    Returns result dict.
    """

    # ── 1. Validity check
    raw_check = cv2.imread(img_path)
    if raw_check is None:
        raise FileNotFoundError(f"Cannot read: {img_path}")

    raw_rgb    = cv2.cvtColor(raw_check, cv2.COLOR_BGR2RGB)
    valid, edge_ratio = is_valid_fingerprint(raw_rgb)

    if not valid:
        print(f"\n⚠️  WARNING: Low edge ratio ({edge_ratio:.4f}).")
        print("   This image may NOT be a fingerprint.")
        print("   Results should be treated with extra caution.\n")

    # ── 2. Ridge quality analysis
    quality, ridge_density, clarity, density = analyze_ridges(raw_rgb)

    # ── 3. Pattern prediction
    _, model_input = preprocess_for_model(img_path)
    preds          = model.predict(model_input, verbose=0)[0]
    pred_idx       = int(np.argmax(preds))
    confidence     = float(np.max(preds))
    pred_pattern   = class_names[pred_idx]

    pattern_probs = {class_names[i]: float(preds[i]) for i in range(len(class_names))}

    # ── 4. Blood group lookup
    bg_probs  = BLOOD_GROUP_PROBS[pred_pattern]
    sorted_bg = sorted(bg_probs.items(), key=lambda x: x[1], reverse=True)
    top_bg    = sorted_bg[0][0]
    top_3     = [f"{g} ({p*100:.1f}%)" for g, p in sorted_bg[:3]]

    info = PATTERN_INFO[pred_pattern]

    # ══════════════════════════════════════════════════════════
    #   PRINTED REPORT
    # ══════════════════════════════════════════════════════════
    W = 64
    print("\n" + "═"*W)
    print("        🩸  BloodPrint ID — Analysis Report")
    print("═"*W)

    # ── Image info
    print(f"\n  📁  File           : {os.path.basename(img_path)}")
    print(f"  🔬  Image Quality  : {quality}  (clarity = {clarity:.1f})")
    print(f"  〰   Ridge Density  : {ridge_density}  (gradient = {density:.1f})")
    valid_label = "✅ Likely fingerprint" if valid else "⚠️  Uncertain — low edge density"
    print(f"  🔍  Edge Ratio     : {edge_ratio:.4f}  {valid_label}")

    # ── Pattern section
    print("\n" + "─"*W)
    print("  🧬  FINGERPRINT PATTERN")
    print("─"*W)

    conf_flag = "✅ High confidence" if confidence >= CONF_THRESHOLD else "⚠️  LOW CONFIDENCE"
    print(f"  Pattern Type   : {info['full_name']}")
    print(f"  Confidence     : {confidence*100:.1f}%  —  {conf_flag}")
    print(f"  Prevalence     : {info['prevalence']}")

    # Word-wrapped description
    print(f"\n  📖  Description:")
    words, line = info['description'].split(), ""
    for w in words:
        if len(line) + len(w) + 1 > 56:
            print(f"      {line}")
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        print(f"      {line}")

    print(f"\n  🔍  Key Characteristics:")
    for ch in info["characteristics"]:
        print(f"      • {ch}")
    print(f"\n  📏  Ridge Count    : {info['ridge_count']}")

    # Pattern probability bars
    print(f"\n  📊  Pattern Probabilities:")
    for pat, prob in sorted(pattern_probs.items(), key=lambda x: x[1], reverse=True):
        bar   = "█" * int(prob * 35)
        arrow = "  ◄ predicted" if pat == pred_pattern else ""
        print(f"      {pat:<8}  {bar:<35}  {prob*100:.1f}%{arrow}")

    # ── Blood group section
    print("\n" + "─"*W)
    print("  🩸  BLOOD GROUP PREDICTION")
    print("─"*W)
    print(f"  Top Prediction : {top_bg}")
    print(f"  Top 3 Likely   : {', '.join(top_3)}")
    print(f"\n  All Blood Group Likelihoods:")
    print(f"  {'Group':<8}  {'Likelihood Bar':<40}  Prob")
    print(f"  {'─'*56}")

    for bg, prob in sorted_bg:
        bar   = "█" * int(prob * 56)
        arrow = "  ◄ Most likely" if bg == top_bg else ""
        print(f"  {bg:<8}  {bar:<40}  {prob*100:.1f}%{arrow}")

    # ── Disclaimer
    print("\n" + "─"*W)
    print("  ⚠️   DISCLAIMER")
    print("─"*W)
    print("""
  Blood group prediction uses STATISTICAL CORRELATIONS
  from published research papers only.

  ❌  NOT a medical or clinical diagnostic tool.
  ❌  Do NOT use this to determine your actual blood group.
  ✅  For educational and research purposes only.
  ✅  Use a certified laboratory test for actual blood typing.
    """)
    print("═"*W)

    result = {
        "file"             : os.path.basename(img_path),
        "pattern"          : pred_pattern,
        "confidence"       : confidence,
        "pattern_probs"    : pattern_probs,
        "blood_group_probs": dict(sorted_bg),
        "top_blood_group"  : top_bg,
        "image_quality"    : quality,
        "ridge_density"    : ridge_density,
        "valid_fingerprint": valid,
    }

    plot_results(result, img_path)
    return result


# ──────────────────────────────────────────────────────────────
# 📊  RESULT CHART  (3 panels)
# ──────────────────────────────────────────────────────────────
def plot_results(result, img_path):
    """
    Three-panel figure:
      Panel 1 — original fingerprint image with pattern label
      Panel 2 — pattern probability bar chart
      Panel 3 — blood group likelihood horizontal bar chart
    """
    fig = plt.figure(figsize=(18, 6))
    fig.patch.set_facecolor('#0d0d1a')

    pattern   = result["pattern"]
    pat_color = PATTERN_INFO[pattern]["color"]

    # ── Panel 1: Image
    ax0 = fig.add_subplot(1, 3, 1)
    ax0.set_facecolor('#1a1a2e')
    raw_gray = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2GRAY)
    ax0.imshow(raw_gray, cmap='gray')
    ax0.axis('off')
    ax0.set_title("Input Fingerprint", color='white', fontsize=12, pad=8)
    ax0.text(
        0.5, 0.04,
        f"{PATTERN_INFO[pattern]['full_name']}  •  {result['confidence']*100:.1f}%",
        transform=ax0.transAxes, ha='center', va='bottom',
        color=pat_color, fontsize=9,
        bbox=dict(facecolor='#000000bb', boxstyle='round,pad=0.3')
    )

    # ── Panel 2: Pattern probabilities
    ax1 = fig.add_subplot(1, 3, 2)
    ax1.set_facecolor('#1a1a2e')

    patterns = list(result["pattern_probs"].keys())
    probs    = [result["pattern_probs"][p] * 100 for p in patterns]
    colors   = [PATTERN_INFO[p]["color"] if p == pattern else '#3a3a5c' for p in patterns]

    bars = ax1.bar(patterns, probs, color=colors, edgecolor='white',
                   linewidth=0.6, width=0.55)

    for bar, prob in zip(bars, probs):
        ax1.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f"{prob:.1f}%", ha='center', va='bottom',
            color='white', fontsize=10, fontweight='bold'
        )

    ax1.set_title("Pattern Classification", color='white', fontsize=12, pad=8)
    ax1.set_ylabel("Probability (%)", color='white', fontsize=9)
    ax1.set_ylim(0, 115)
    ax1.tick_params(colors='white', labelsize=10)
    ax1.spines[:].set_color('#444')

    # ── Panel 3: Blood group likelihoods
    ax2 = fig.add_subplot(1, 3, 3)
    ax2.set_facecolor('#1a1a2e')

    bg_items   = sorted(result["blood_group_probs"].items(),
                        key=lambda x: x[1], reverse=True)
    bg_names   = [x[0] for x in bg_items]
    bg_probs   = [x[1] * 100 for x in bg_items]
    bar_colors = plt.cm.RdYlGn(np.linspace(0.2, 0.85, len(bg_names)))

    bars2 = ax2.barh(bg_names, bg_probs, color=bar_colors,
                     edgecolor='white', linewidth=0.4, height=0.65)

    for bar, prob in zip(bars2, bg_probs):
        ax2.text(
            prob + 0.3, bar.get_y() + bar.get_height() / 2,
            f"{prob:.1f}%", va='center', color='white', fontsize=9
        )

    ax2.set_title(
        f"Blood Group Likelihood\n(Pattern: {pattern})",
        color='white', fontsize=12, pad=8
    )
    ax2.set_xlabel("Likelihood (%)", color='white', fontsize=9)
    ax2.set_xlim(0, 38)
    ax2.tick_params(colors='white', labelsize=10)
    ax2.spines[:].set_color('#444')

    plt.tight_layout(pad=2.5)

    base_name = os.path.splitext(os.path.basename(img_path))[0]
    out = f"{RESULTS_DIR}/result_{base_name}.png"
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#0d0d1a')
    plt.show()
    print(f"\n📊 Result chart saved → {out}")


# ──────────────────────────────────────────────────────────────
# ▶  MAIN
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🩸  BloodPrint ID — Step 3: Prediction")
    print("="*60)

    # ── Load model
    if not os.path.exists(MODEL_SAVE):
        print(f"❌ Model not found at {MODEL_SAVE}")
        print("   Run train_model.py first.")
        exit(1)

    print(f"\n📂 Loading model  → {MODEL_SAVE}")
    model = load_model(MODEL_SAVE)

    # ── Load class names from config
    if os.path.exists(CONFIG_SAVE):
        with open(CONFIG_SAVE) as f:
            config = json.load(f)
        class_names = config["class_names"]
        print(f"📂 Config loaded  → class_names: {class_names}")
    else:
        class_names = ['loop', 'whorl', 'arch']
        print(f"⚠️  Config not found — using default: {class_names}")

    print("\n" + "─"*60)
    print("  Model ready. Enter image paths to predict.")
    print("  Type  'quit'  to exit.")
    print("─"*60)

    # ── Prediction loop
    while True:
        img_path = input("\n  Enter fingerprint image path: ").strip()

        if img_path.lower() in ('quit', 'exit', 'q'):
            break

        if not os.path.exists(img_path):
            print(f"  ❌ File not found: {img_path}")
            continue

        try:
            predict_and_report(img_path, model, class_names)
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n✅ Session ended.")
    print(f"   All charts saved to: {RESULTS_DIR}/\n")
