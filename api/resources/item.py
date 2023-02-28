"""Item resource module."""
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.db import db
from api.models import ItemModel
from api.schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    """Item resource."""
    @blp.response(200, ItemSchema)
    @blp.alt_response(404, description="Item not found.")
    @jwt_required()
    def get(self, item_id: int) -> tuple[dict, int]:
        """Get an item.

        Args:
            item_id (int): item id

        Returns:
            tuple[dict, int]: response message and status code or item and status code
        """
        item = ItemModel.query.filter_by(id=item_id).first()
        if item is None:
            abort(404, message="Item not found.")
        return item, 200

    @blp.response(202)
    @blp.alt_response(404, description="Item not found.")
    @blp.alt_response(500, description="An error occurred deleting the item.")
    @jwt_required()
    def delete(self, item_id: int) -> tuple[dict, int]:
        """Delete an item.

        Args:
            item_id (int): item id

        Returns:
            tuple[dict, int]: response message and status code
        """
        try:
            item = ItemModel.query.filter_by(id=item_id).first()
            if item is None:
                abort(404, message="Item not found.")
            db.session.delete(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred deleting the item.")
        return {"message": "Item deleted."}, 202

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    @blp.alt_response(400, description="Item must have a name and a price.")
    @jwt_required()
    def put(self, item_data: dict, item_id: int) -> tuple[dict, int]:
        """Update an item.

        Args:
            item_data (dict): item data
            item_id (int): item id

        Returns:
            tuple[dict, int]: response message and status code
        """
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

        return item, 200


@blp.route("/item")
class ItemList(MethodView):
    """ ItemList resource. """
    @blp.response(200, ItemSchema(many=True))
    @jwt_required()
    def get(self) -> tuple[list[ItemModel], int]:
        """Get all items.

        Returns:
            tuple[list[ItemModel], int]: response message and status code
        """
        return ItemModel.query.all(), 200

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    @blp.alt_response(500, description="An error occurred while inserting the item.")
    @blp.alt_response(400, description="Item must have a name and a price.")
    @blp.alt_response(409, description="An item with that name already exists.")
    @jwt_required(fresh=True)
    def post(self, item_data: dict) -> tuple[dict, int]:
        """Create an item.

        Args:
            item_data (dict): item data

        Returns:
            tuple[dict, int]: response message and status code
        """
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

        return item, 201
