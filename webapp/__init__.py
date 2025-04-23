import os

from dotenv import load_dotenv
from flask import Flask

from .utils import db

from . import auth, routes


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        MYSQL_HOST=os.environ.get("MYSQL_HOST"),
        MYSQL_USER=os.environ.get("MYSQL_USER"),
        MYSQL_PASSWORD=os.environ.get("MYSQL_PASSWORD"),
        MYSQL_DB=os.environ.get("MYSQL_DB"),
        MYSQL_CURSORCLASS=os.environ.get("MYSQL_CURSORCLASS"),
    )

    with app.app_context():
        db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(routes.bp)

    app.add_url_rule("/", endpoint="index")

    return app
