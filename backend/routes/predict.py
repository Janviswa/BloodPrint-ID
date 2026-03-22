# routes/predict.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Prediction
from predictor import run_prediction
import os, json, uuid

predict_bp = Blueprint('predict', __name__)
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED = {'image/jpeg','image/png','image/bmp','image/tiff','image/webp'}

@predict_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    print("🔥 PREDICT API CALLED")

    uid = int(get_jwt_identity())
    print("User ID:", uid)

    if 'file' not in request.files:
        print("❌ No file")
        return jsonify(error='No file uploaded.'), 400

    f = request.files['file']
    print("📁 File received:", f.filename, f.content_type)

    if f.content_type not in ALLOWED:
        print("❌ Invalid file type")
        return jsonify(error='Invalid file'), 400

    ext = os.path.splitext(f.filename)[1] or '.jpg'
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    f.save(path)

    print("💾 File saved at:", path)

    try:
        print("🚀 Running prediction...")
        
        result = run_prediction(path)   # ✅ REAL MODEL CALL
        
        print("✅ Prediction done:", result)

    except Exception as e:
        print("💥 ERROR IN MODEL:", str(e))
        return jsonify(error=str(e)), 500
        
    rec = Prediction(
        user_id=uid,
        filename=f.filename,
        pattern=result['pattern'],
        confidence=result['confidence'],
        top_bg=result['top_blood_group'],
        image_quality=result['image_quality'],
        ridge_density=result['ridge_density'],
        valid_fp=result['valid_fingerprint'],
        result_json=json.dumps(result),
    )
    db.session.add(rec)
    db.session.commit()

    result['id'] = rec.id
    result['filename'] = f.filename

    return jsonify(result), 200