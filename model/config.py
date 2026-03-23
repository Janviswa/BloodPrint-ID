# -*- coding: utf-8 -*-
"""
config.py — Shared constants for BloodPrint ID
────────────────────────────────────────────────
Imported by all three modules:
    feature_extraction.py  →  from config import *
    train_model.py         →  from config import *
    prediction.py          →  from config import *
"""

import os

# ==============================================================
# ⚙️  PATHS  — edit only here, reflects everywhere
# ==============================================================
DATASET_PATH  = "/content/drive/MyDrive/SOCOFing_dataset"
CLUSTERS_DIR  = "/content/clusters"
MODEL_SAVE    = "/content/bloodprint_efficientnet.h5"
CONFIG_SAVE   = "/content/model_config.json"
FEATURES_PATH = "/content/features.npy"
NAMES_PATH    = "/content/image_names.npy"
RESULTS_DIR   = "/content/results"

# ==============================================================
# ⚙️  HYPERPARAMETERS
# ==============================================================
NUM_CLUSTERS     = 3
IMG_SIZE         = (224, 224)
BATCH_SIZE       = 32
EPOCHS           = 10
CONF_THRESHOLD   = 0.55
VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')

# ==============================================================
# 📖  FINGERPRINT PATTERN INFO
# ==============================================================
PATTERN_INFO = {
    "loop": {
        "full_name"      : "Loop Pattern",
        "prevalence"     : "~65% of population — most common pattern",
        "description"    : (
            "Ridge lines enter from one side of the finger, curve around "
            "a central core point, and exit from the same side they entered. "
            "Sub-types: Ulnar Loop (opens toward little finger) and "
            "Radial Loop (opens toward thumb). Loops are the most "
            "frequently observed pattern across all ethnicities."
        ),
        "characteristics": [
            "Exactly one delta point visible",
            "Ridges open on one side only",
            "Core forms a rounded loop shape",
            "Ridge count measured between core and delta",
            "Ulnar loops are far more common than radial loops",
        ],
        "ridge_count": "Typically 5–15 ridges between delta and core",
        "color"      : "#4cc9f0",
    },
    "whorl": {
        "full_name"      : "Whorl Pattern",
        "prevalence"     : "~30% of population — second most common",
        "description"    : (
            "Ridges form complete circular or spiral circuits around a "
            "central core. Sub-types: Plain Whorl, Central Pocket Loop "
            "Whorl, Double Loop Whorl (two separate loop systems), and "
            "Accidental Whorl (does not fit other categories)."
        ),
        "characteristics": [
            "Two delta points present (left and right)",
            "At least one ridge completes a full 360° circuit",
            "Core is centrally positioned",
            "Can appear as concentric circles or tight spiral",
            "Double loop whorl contains two cores",
        ],
        "ridge_count": "Inner tracing method used (inner / meeting / outer)",
        "color"      : "#f72585",
    },
    "arch": {
        "full_name"      : "Arch Pattern",
        "prevalence"     : "~5% of population — rarest pattern",
        "description"    : (
            "The simplest fingerprint pattern. Ridges enter from one side, "
            "rise gently in the center like a wave or tent, and exit on the "
            "opposite side. No delta points or core present. "
            "Sub-types: Plain Arch (gentle wave) and Tented Arch "
            "(sharp upward thrust in the center)."
        ),
        "characteristics": [
            "No delta points whatsoever",
            "No core present",
            "Ridges flow smoothly side-to-side",
            "Center ridges rise to form a gentle or sharp peak",
            "Tented arch has an upright rod or spike at center",
        ],
        "ridge_count": "No ridge count possible (no delta or core)",
        "color"      : "#7bed9f",
    },
}

# ==============================================================
# 🩸  BLOOD GROUP PROBABILITY TABLE
# Sources: Dogra et al. (2014), Nayak et al. (2010),
#          Igbigbi & Thumb (2002), Cummins & Midlo (1961)
# Statistical correlations only — NOT diagnostic.
# ==============================================================
_RAW_BG_PROBS = {
    "loop": {
        "O+" : 0.28, "O-" : 0.08,
        "A+" : 0.22, "A-" : 0.06,
        "B+" : 0.16, "B-" : 0.05,
        "AB+": 0.10, "AB-": 0.05,
    },
    "whorl": {
        "O+" : 0.18, "O-" : 0.05,
        "A+" : 0.15, "A-" : 0.04,
        "B+" : 0.28, "B-" : 0.08,
        "AB+": 0.14, "AB-": 0.08,
    },
    "arch": {
        "O+" : 0.18, "O-" : 0.06,
        "A+" : 0.22, "A-" : 0.08,
        "B+" : 0.12, "B-" : 0.04,
        "AB+": 0.20, "AB-": 0.10,
    },
}

def _normalize(d):
    """Auto-normalize so values always sum to 1.0."""
    t = sum(d.values())
    return {k: round(v / t, 6) for k, v in d.items()}

BLOOD_GROUP_PROBS = {k: _normalize(v) for k, v in _RAW_BG_PROBS.items()}

# Create results directory on import
os.makedirs(RESULTS_DIR, exist_ok=True)
