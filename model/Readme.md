# 🧠 BloodPrint ID — Model Training

This folder contains the full training pipeline for the fingerprint classification model.

## 📦 Dataset

This project uses the **SOCOFing (Sokoto Coventry Fingerprint Dataset)**.

- 🔗 Download: [Kaggle — SOCOFing](https://www.kaggle.com/datasets/ruizgara/socofing)
- ~6000 fingerprint images in `.BMP` format
- After downloading, update `DATASET_PATH` in `config.py`

## 🗂️ Files

| File | Purpose |
|------|---------|
| `config.py` | All paths and hyperparameters — edit this first |
| `feature_extraction.py` | Step 1 — extract features + cluster into loop/whorl/arch |
| `train_model.py` | Step 2 — train EfficientNetB0 classifier |
| `prediction.py` | Step 3 — test predictions locally |

## 🚀 How to Train (Google Colab recommended)

### Step 1 — Setup
```bash
pip install tensorflow opencv-python scikit-learn matplotlib seaborn
```

### Step 2 — Edit `config.py`
```python
DATASET_PATH = "/content/drive/MyDrive/SOCOFing_dataset"  # your dataset path
```

### Step 3 — Run in order
```bash
# Extract features and cluster images
python feature_extraction.py

# Open results/cluster_inspection.png
# Identify which cluster = loop / whorl / arch
# Then train:
python train_model.py

# Test predictions:
python prediction.py
```

## 📤 Output Files

After training, copy these files to `backend/`:

```
bloodprint_efficientnet.h5   →  backend/
model_config.json            →  backend/
```

Then convert to TFLite for deployment:
```bash
cd backend
python convert_model.py
# Produces model.tflite → used by the Flask API on Render
```

## ⚙️ Model Architecture

```
EfficientNetB0 (ImageNet weights, frozen)
  → GlobalAveragePooling2D
  → BatchNormalization
  → Dense(256, relu) → Dropout(0.4)
  → Dense(128, relu) → Dropout(0.3)
  → Dense(3, softmax)        # loop / whorl / arch
```

Training uses two phases:
1. **Phase 1** — head only, base frozen, `lr=1e-3`
2. **Phase 2** — fine-tune top 20 EfficientNet layers, `lr=1e-5`
