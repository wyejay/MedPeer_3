import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key'),
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        MAX_CONTENT_LENGTH = int(os.environ.get('UPLOAD_MAX_SIZE_MB', '20')) * 1024 * 1024,
    )
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins='*')

    from . import models, routes, sockets, admin
    app.register_blueprint(routes.bp)
    app.register_blueprint(admin.bp, url_prefix='/admin')

    # ensure upload folder exists for local dev when S3 not configured
    os.makedirs(app.config.get('LOCAL_UPLOAD_FOLDER','uploads'), exist_ok=True)

    return app
