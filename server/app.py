from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter.errors import RateLimitExceeded

from routes.user_routes import user_bp
from routes.camera_log_routes import camera_log_bp
from routes.camera_routes import camera_bp

from limiter import limiter

from sqlalchemy import event
from sqlalchemy.engine import Engine

import sqlite3

from database import db

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from models.camera_log import CameraLog
from models.camera import Camera
from models.user import User

from pathlib import Path

import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = str(Path.home() / "Desktop" / "diploment-proekt" / "fridge-uni-project-main" / "server")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, os.environ.get('DB_PATH', 'camera.db'))}"
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
app.config["JWT_COOKIE_SECURE"] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)


db.init_app(app)
Bcrypt(app)
JWTManager(app)
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://192.168.0.238:5173'])
limiter.init_app(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Delete Old Logs (more than 1 year)
def delete_old_logs():
    with app.app_context():
        cutoff = datetime.utcnow() - timedelta(days=365)
        CameraLog.query.filter(CameraLog.timestamp < cutoff).delete()
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_logs, "interval", days=1)
scheduler.start()

app.register_blueprint(user_bp)
app.register_blueprint(camera_log_bp)
app.register_blueprint(camera_bp)

print(f"Database path: {os.path.join(BASE_DIR, 'camera.db')}")

with app.app_context():
    db.create_all()

@app.errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    return jsonify({"message": "Прекалено много опити. Моля опитайте по-късно"}), 429

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
