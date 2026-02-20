from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():

    app = Flask(
        __name__,
        static_folder=os.path.join(os.getcwd(), "static"),
        static_url_path="/static"
    )

    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = "routes.login"

    from app.routes import routes
    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()

    return app