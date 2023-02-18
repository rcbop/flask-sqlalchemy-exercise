from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.db import db
from api.models import ItemModel
from api.schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    @blp.alt_response(404, description="Item not found.")
    @jwt_required()
    def get(self, item_id):
        item = ItemModel.query.filter_by(id=item_id).first()
        if item is None:
            abort(404, message="Item not found.")
        return item

    @blp.response(202)
    @blp.alt_response(404, description="Item not found.")
    @blp.alt_response(500, description="An error occurred deleting the item.")
    @jwt_required()
    def delete(self, item_id):
        try:
            item = ItemModel.query.filter_by(id=item_id).first()
            if item is None:
                abort(404, message="Item not found.")
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted."}, 202
        except SQLAlchemyError:
            abort(500, message="An error occurred deleting the item.")

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    @blp.alt_response(400, description="Item must have a name and a price.")
    @jwt_required()
    def put(self, item_data, item_id):
        if "name" not in item_data:
            abort(400, message="Item must have a name.")
        if "price" not in item_data:
            abort(400, message="Item must have a price.")

        item = ItemModel.query.filter_by(id=item_id).first()

        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    @jwt_required()
    def get(self):
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    @blp.alt_response(500, description="An error occurred while inserting the item.")
    @blp.alt_response(400, description="Item must have a name and a price.")
    @blp.alt_response(409, description="An item with that name already exists.")
    @jwt_required(fresh=True)
    def post(self, item_data):
        if "name" not in item_data or "price" not in item_data:
            abort(400, message="Item must have a name and a price.")
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(
                409,
                message="An item with that name already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item
