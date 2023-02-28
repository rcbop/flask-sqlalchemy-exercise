""" Store resource """
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from api.db import db
from api.models import StoreModel
from api.schemas import StoreSchema


blp = Blueprint("Stores", "stores", description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    """ Store resource """
    @blp.response(200, StoreSchema)
    @blp.alt_response(404, description="Store not found.")
    @jwt_required()
    def get(self, store_id: int) -> tuple[dict, int]:
        """Get a store

        Args:
            store_id (int): store id

        Returns:
            tuple[dict, int]: response message and status code or store and status code
        """
        store = db.session.query(StoreModel).filter_by(id=store_id).first()
        if store is None:
            abort(404, message="Store not found.")
        return store, 200

    @blp.response(202)
    @blp.alt_response(404, description="Store not found.")
    @jwt_required()
    def delete(self, store_id: int) -> tuple[dict, int]:
        """Delete a store

        Args:
            store_id (int): store id

        Returns:
            tuple[dict, int]: response message and status code
        """
        store = db.session.query(StoreModel).filter_by(id=store_id).first()
        if store is None:
            abort(404, message="Store not found.")
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}, 202


@blp.route("/store")
class StoreList(MethodView):
    """ Store list resource """
    @blp.response(200, StoreSchema(many=True))
    @jwt_required()
    def get(self) -> tuple[list[dict], int]:
        """Get all stores

        Returns:
            tuple[list[dict], int]: list of stores and status code
        """
        return StoreModel.query.all(), 200

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    @blp.alt_response(400, description="Store must have a name.")
    @blp.alt_response(409, description="A store with that name already exists.")
    @blp.alt_response(500, description="An error occurred creating the store.")
    @jwt_required()
    def post(self, store_data: dict) -> tuple[dict, int]:
        """Create a store

        Args:
            store_data (dict): store data

        Returns:
            tuple[dict, int]: store and status code
        """
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

        return store, 201
