from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt, jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from api.db import db
from api.models import StoreModel
from api.schemas import StoreSchema


blp = Blueprint("Stores", "stores", description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    @blp.alt_response(404, description="Store not found.")
    @jwt_required()
    def get(self, store_id):
        store = db.session.query(StoreModel).filter_by(id=store_id).first()
        if store is None:
            abort(404, message="Store not found.")
        return store

    @blp.response(202)
    @blp.alt_response(404, description="Store not found.")
    @jwt_required()
    def delete(self, store_id):
        store = db.session.query(StoreModel).filter_by(id=store_id).first()
        if store is None:
            abort(404, message="Store not found.")
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}, 202


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    @jwt_required()
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    @blp.alt_response(400, description="Store must have a name.")
    @blp.alt_response(409, description="A store with that name already exists.")
    @blp.alt_response(500, description="An error occurred creating the store.")
    @jwt_required()
    def post(self, store_data):
        try:
            store = StoreModel(**store_data)
            if 'name' not in store_data:
                abort(400, message="Store must have a name.")
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                409,
                message="A store with that name already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the store.")

        return store
