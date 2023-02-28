""" Flask app and API registration. """
import os
import secrets

import redis
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from rq import Queue

from api.auth.blocklist import BLOCKLIST
from api.db import db
from api.resources.healthcheck import blp as HealthCheckBlueprint
from api.resources.item import blp as ItemBlueprint
from api.resources.store import blp as StoreBlueprint
from api.resources.tag import blp as TagBlueprint
from api.resources.user import blp as UserBlueprint


def create_app(db_url: str | None = None, jwt_secret: str | None = None) -> Api:
    """Create a Flask app and register the API.

    Args:
        db_url (str | None, optional): Database URL. Defaults to None.
        jwt_secret (str | None, optional): JWT secret key. Defaults to None.

    Returns:
        Api: The API.
    """
    app = Flask(__name__)

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_connection = redis.from_url(redis_url)
    app.queue = Queue("emails", connection=redis_connection)  # type: ignore
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["JWT_SECRET_KEY"] = jwt_secret or os.getenv(
        "JWT_SECRET_KEY", str(secrets.SystemRandom().getrandbits(256))
    )

    db.init_app(app)
    Migrate(app, db)

    api = Api(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def verify_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"description": "The token has expired", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Signature verification failed",
                    "error": "invalid_token",
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked", "error": "token_revoked"}
            ),
            401,
        )

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(HealthCheckBlueprint)

    return app


if __name__ == "__main__":
    load_dotenv()
    app = create_app()
    app.run(debug=True)
