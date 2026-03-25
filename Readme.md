<h1>🩸 BloodPrint ID</h1>

> Fingerprint pattern classification with statistical blood group correlation — built for educational and research purposes.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-blood--print--id.vercel.app-blue?style=for-the-badge&logo=vercel)](https://blood-print-id.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://render.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![YouTube](https://img.shields.io/badge/Demo%20Video-YouTube-FF0000?style=for-the-badge&logo=youtube)](https://youtu.be/vyVpR04w9-U)
[![Gmail](https://img.shields.io/badge/Contact-jananiviswa05@gmail.com-D14836?style=for-the-badge&logo=gmail)](mailto:jananiviswa05@gmail.com)

---

## 🌐 Live Demo

🔗 **Website:** [https://blood-print-id.vercel.app](https://blood-print-id.vercel.app)

🎥 **Demo Video:** [Watch on YouTube](https://youtu.be/vyVpR04w9-U)

---

## 📌 Overview

**BloodPrint ID** is a full-stack AI web application that analyzes fingerprint images to classify their pattern type (Loop, Whorl, or Arch) and provides statistical blood group likelihood based on published dermatoglyphic research.

> ⚠️ **Not a medical tool.** All blood group correlations are statistical estimates from published research — not a clinical diagnosis.

---

## ✨ Features

- 🔍 **Fingerprint Pattern Classification** — Loop, Whorl, Arch using EfficientNetB0
- 🩸 **Blood Group Statistical Correlation** — based on published dermatoglyphic studies
- 📊 **Image Quality Metrics** — clarity score, ridge density, edge ratio
- 📄 **PDF Report Generation** — downloadable professional report per analysis
- 🗂️ **Analysis History** — view and manage past predictions
- 🔐 **JWT Authentication** — secure user accounts
- 🌙 **Dark Mode UI** — sleek React frontend

---

## 🛠️ Tech Stack

| Layer     | Technology |
|-----------|-----------|
| Frontend  | React, Vite, Axios |
| Backend   | Flask, Python 3.11 |
| ML Model  | EfficientNetB0 → TFLite |
| Database  | PostgreSQL (Supabase) |
| PDF       | ReportLab |
| Auth      | Flask-JWT-Extended |
| Hosting   | Vercel (frontend) · Render (backend) |

---

## 🏗️ Project Structure

```
BloodPrint-ID/
├── backend/
│   ├── app.py                  # Flask app factory
│   ├── predictor.py            # TFLite inference + image metrics
│   ├── report_generator.py     # PDF generation (ReportLab)
│   ├── convert_model.py        # H5 → TFLite conversion utility
│   ├── models.py               # SQLAlchemy models
│   ├── extensions.py           # DB + JWT init
│   ├── routes/
│   │   ├── auth.py             # Register / Login
│   │   ├── predict.py          # POST /api/predict
│   │   ├── history.py          # GET /api/history
│   │   └── report.py           # GET /api/report/<id>
│   ├── model.tflite            # Optimised TFLite model
│   ├── requirements.txt
│   └── Procfile
└── frontend/
    └── src/
        ├── pages/
        │   ├── Predict.jsx     # Main analysis page
        │   ├── History.jsx     # Past analyses
        │   ├── Research.jsx    # Research references
        │   └── Settings.jsx    # User settings
        ├── context/
        │   └── AuthContext.jsx
        └── utils/
            └── api.js          # Axios instance
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database (e.g. Supabase)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in DATABASE_URL, SECRET_KEY, JWT_SECRET

python app.py
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:5000/api" > .env

npm run dev
```

### Convert Model (if needed)

```bash
cd backend
python convert_model.py
# Generates model.tflite from bloodprint_efficientnet.h5
```

---

## 🌐 Deployment

| Service  | Purpose | Config |
|----------|---------|--------|
| **Vercel** | Frontend hosting | `VITE_API_URL` env var |
| **Render** | Backend hosting | `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET` env vars |
| **Supabase** | PostgreSQL database | Connection string in `DATABASE_URL` |

---

## 📚 Research References

1. Dogra, T.D. et al. (2014). *Fingerprint patterns and ABO blood group correlation.* Journal of Forensic Medicine and Toxicology.
2. Nayak, V.C. et al. (2010). *Correlating fingerprint patterns with blood groups.* Journal of Forensic and Legal Medicine.
3. Igbigbi, P.S. & Thumb, B. (2002). *Dermatoglyphic patterns of Ugandan and Tanzanian subjects.* West African Journal of Medicine.
4. Cummins, H. & Midlo, C. (1961). *Finger Prints, Palms and Soles.* Dover Publications.

---

## ⚖️ Disclaimer

This project is for **educational and research purposes only**. Blood group predictions are based on statistical correlations from published dermatoglyphic research and do **not** constitute a medical diagnosis. Always use a certified laboratory blood typing test for actual blood group determination.

---

## ⭐ Support

If you found this project helpful or interesting, please consider giving it a **star** ⭐ — it helps others discover the project and motivates further development!

[![Star this repo](https://img.shields.io/github/stars/Janviswa/BloodPrint-ID?style=social)](https://github.com/Janviswa/BloodPrint-ID)

> 💬 Have feedback or questions? Reach out at [jananiviswa05@gmail.com](mailto:jananiviswa05@gmail.com)

---

## 👩‍💻 Author

**Janani V**

[![GitHub](https://img.shields.io/badge/GitHub-Janiswa-181717?style=flat-square&logo=github)](https://github.com/Janiswa)
[![Gmail](https://img.shields.io/badge/Gmail-jananiviswa05@gmail.com-D14836?style=flat-square&logo=gmail)](mailto:jananiviswa05@gmail.com)
[![YouTube](https://img.shields.io/badge/YouTube-Demo-FF0000?style=flat-square&logo=youtube)](https://youtu.be/vyVpR04w9-U)

---

<p align="center">Made with ❤️ for research · Not for clinical use</p>
