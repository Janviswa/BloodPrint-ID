# models.py
from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(120), unique=True, nullable=False)  # email or username
    full_name     = db.Column(db.String(120), nullable=True)                # display name
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    predictions   = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':         self.id,
            'username':   self.username,
            'full_name':  self.full_name or self.username,
            'created_at': self.created_at.isoformat(),
        }


class Prediction(db.Model):
    __tablename__ = 'predictions'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename      = db.Column(db.String(256))
    pattern       = db.Column(db.String(32))
    confidence    = db.Column(db.Float)
    top_bg        = db.Column(db.String(8))
    image_quality = db.Column(db.String(16))
    ridge_density = db.Column(db.String(16))
    valid_fp      = db.Column(db.Boolean)
    result_json   = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.id,
            'filename':     self.filename,
            'pattern':      self.pattern,
            'confidence':   self.confidence,
            'top_bg':       self.top_bg,
            'image_quality':self.image_quality,
            'ridge_density':self.ridge_density,
            'valid_fp':     self.valid_fp,
            'created_at':   self.created_at.strftime('%Y-%m-%d %H:%M'),
        }