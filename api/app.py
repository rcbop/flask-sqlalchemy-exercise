import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from api.db import db
from api.resources.item import blp as ItemBlueprint
from api.resources.store import blp as StoreBlueprint
from api.resources.tag import blp as TagBlueprint


def create_app(db_url: str | None = None, jwt_secret: str | None = None) -> Api:
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db")
    app.config["JWT_SECRET_KEY"] = jwt_secret or os.getenv(
        "JWT_SECRET_KEY", "super-secret")
    db.init_app(app)

    with app.app_context():
        db.create_all()

    api = Api(app)

    jwt = JWTManager(app)

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    return app
