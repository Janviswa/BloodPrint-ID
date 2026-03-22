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
    uid = int(get_jwt_identity())

    if 'file' not in request.files:
        return jsonify(error='No file uploaded.'), 400

    f = request.files['file']
    if f.content_type not in ALLOWED:
        return jsonify(error='File must be an image (JPG, PNG, BMP, TIFF).'), 400

    ext = os.path.splitext(f.filename)[1] or '.jpg'
    safe_name = f"{uid}_{uuid.uuid4().hex[:8]}{ext}"
    path = os.path.join(UPLOAD_DIR, safe_name)
    f.save(path)

    try:
        print("Running prediction on:", path)
        result = run_prediction(path)
        print("RESULT:", result)

    except Exception as e:
        import traceback
        traceback.print_exc()   # 👈 IMPORTANT
        print("ERROR:", str(e))

        if os.path.exists(path):
            os.remove(path)

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