# app.py
from flask import Flask
from flask_cors import CORS
from extensions import db, jwt
from routes.auth    import auth_bp
from routes.predict import predict_bp
from routes.history import history_bp
from routes.report  import report_bp
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']              = os.environ.get('SECRET_KEY', 'bloodprint-dev-secret-change-in-prod')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"sslmode": "require"}
    }
    app.config['JWT_SECRET_KEY']          = os.environ.get('JWT_SECRET', 'bloodprint-jwt-secret-key-32bytes!!')
    app.config['JWT_ACCESS_TOKEN_EXPIRES']= False
    app.config['MAX_CONTENT_LENGTH']      = 16 * 1024 * 1024

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp,    url_prefix='/api/auth')
    app.register_blueprint(predict_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    app.register_blueprint(report_bp,  url_prefix='/api')

    with app.app_context():
        db.create_all()
        _migrate_add_full_name()
        _seed_demo()

    return app

def _migrate_add_full_name():
    """Add full_name column if it doesn't exist (safe migration)."""
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(120)"))
            conn.commit()
    except Exception:
        pass  # column already exists

def _seed_demo():
    from models import User
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(username='demo').first():
        db.session.add(User(
            username='demo',
            full_name='Demo User',
            password_hash=generate_password_hash('demo123')
        ))
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)