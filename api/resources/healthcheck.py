from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import text

from api.db import db

blp = Blueprint("healthcheck", "healthcheck", description="Check connections to database")

@blp.route("/healthcheck")
class HealthCheck(MethodView):
    def get(self):
        try:
            query = text("SELECT 1")
            db.session.execute(query)
            return {"message": "OK"}
        except Exception as err:
            return {"message": f"Error {err}"}, 500