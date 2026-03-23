# routes/report.py
from flask import Blueprint, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Prediction, User
from report_generator import generate_pdf
import json

report_bp = Blueprint('report', __name__)

@report_bp.route('/report/<int:rid>', methods=['GET'])
@jwt_required()
def download_report(rid):
    uid  = int(get_jwt_identity())
    rec  = Prediction.query.filter_by(id=rid, user_id=uid).first_or_404()
    user = User.query.get(uid)

    result = json.loads(rec.result_json)
    result['filename']   = rec.filename
    result['created_at'] = rec.created_at.strftime('%Y-%m-%d %H:%M:%S')
    result['username']   = user.username if user else 'N/A'

    # Use full_name (display name) if set, else fall back to cleaned username
    if user and user.full_name and user.full_name.strip():
        display_name = user.full_name.strip()
    else:
        username = user.username if user else ''
        display_name = username.split('@')[0].capitalize() if '@' in username else username.capitalize()

    pdf_path = generate_pdf(result, rid, display_name=display_name)
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'BloodPrint_Report_{rid}.pdf'
    )