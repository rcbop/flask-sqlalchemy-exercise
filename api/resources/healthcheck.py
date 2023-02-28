""" Healthcheck resource """
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from api.db import db

blp = Blueprint("healthcheck", "healthcheck", description="Check connections to database")

@blp.route("/healthcheck")
class HealthCheck(MethodView):
    """ Healthcheck resource """
    def get(self) -> tuple[dict, int]:
        """ Check if database is up """
        try:
            query = text("SELECT 1")
            db.session.execute(query)
            return {"message": "OK"}, 200
        except SQLAlchemyError as err:
            return {"message": f"Internal error: {err}"}, 500
