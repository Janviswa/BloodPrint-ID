# routes/history.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Prediction
import json

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    uid  = int(get_jwt_identity())
    rows = Prediction.query.filter_by(user_id=uid).order_by(Prediction.id.desc()).all()
    return jsonify([r.to_dict() for r in rows]), 200


@history_bp.route('/history/<int:rid>', methods=['GET'])
@jwt_required()
def get_one(rid):
    uid = int(get_jwt_identity())
    rec = Prediction.query.filter_by(id=rid, user_id=uid).first_or_404()
    data = rec.to_dict()
    data['result'] = json.loads(rec.result_json)
    return jsonify(data), 200


@history_bp.route('/history', methods=['DELETE'])
@jwt_required()
def clear_history():
    uid = int(get_jwt_identity())
    Prediction.query.filter_by(user_id=uid).delete()
    db.session.commit()
    return jsonify(message='History cleared.'), 200


@history_bp.route('/history/<int:rid>', methods=['DELETE'])
@jwt_required()
def delete_one(rid):
    uid = int(get_jwt_identity())
    rec = Prediction.query.filter_by(id=rid, user_id=uid).first_or_404()
    db.session.delete(rec)
    db.session.commit()
    return jsonify(message='Record deleted.'), 200
