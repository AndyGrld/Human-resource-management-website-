from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask
from flask_caching import Cache
from os import path


db = SQLAlchemy()
DB_NAME = 'database.db'
cache = Cache(config={'CACHE_TYPE': 'simple'})


def create_app():
    app = Flask(__name__)
    UPLOAD_FOLDER = 'static/profiles/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = 'gaa gaa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    login_manager = LoginManager()
    # if not logged in view auth.login
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from mainApp.views import views
    from mainApp.auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    create_database(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    cache.init_app(app)

    return app


def create_database(app):
    if not path.exists('mainApp/' + DB_NAME):
        with app.app_context():
            db.create_all()
