""" tag resource """
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from api.db import db
from api.models import TagModel, StoreModel, ItemModel
from api.schemas import TagSchema, TagAndItemSchema

blp = Blueprint('Tags', 'tags', description='Operations on tags')

@blp.route("/stores/<int:store_id>/tag")
class TagsInStore(MethodView):
    """ Tags in store resource """
    @blp.response(200, TagSchema(many=True))
    @blp.alt_response(404, description="Store not found.")
    @jwt_required()
    def get(self, store_id: int) -> tuple[list[dict], int]:
        """Get all tags in a store

        Args:
            store_id (int): store id

        Returns:
            tuple[list[dict], int]: list of tags and status code
        """
        store = db.session.query(StoreModel).filter_by(id=store_id).first()
        if not store:
            abort(404, message="Store not found.")
        return store.tags.all(), 200

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    @blp.alt_response(400, description="Tag name is required.")
    @blp.alt_response(404, description="Store not found.")
    @blp.alt_response(409, description="Tag with name already exists in that store.")
    @blp.alt_response(500, description="Database error.")
    @jwt_required()
    def post(self, new_tag: dict, store_id: int) -> tuple[dict, int]:
        """Create a new tag in a store

        Args:
            new_tag (dict): new tag data
            store_id (int): store id

        Returns:
            tuple[dict, int]: response message and status code or tag and status code
        """
        try:
            store = db.session.query(StoreModel).filter_by(id=store_id).first()
            if 'name' not in new_tag:
                abort(400, message="Tag name is required.")
            if not store:
                abort(404, message="Store not found.")
            if db.session.query(TagModel).filter_by(name=new_tag['name'], store_id=store_id).first():
                abort(409, message="Tag with name already exists in that store.")
            tag = TagModel(**new_tag, store_id=store_id)
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            abort(500, message=f"Database error: {err}")
        return tag, 201

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    """ Link tags to item resource """
    @blp.response(201, TagSchema(many=True))
    @blp.alt_response(404, description="Item or tag not found.")
    @blp.alt_response(500, description="Database error.")
    @jwt_required()
    def post(self, item_id: int, tag_id: int) -> tuple[dict, int]:
        """Link a tag to an item

        Args:
            item_id (int): item id
            tag_id (int): tag id

        Returns:
            tuple[dict, int]: response message and status code or tags and status code
        """
        try:
            item = db.session.query(ItemModel).filter_by(id=item_id).first()
            tag = db.session.query(TagModel).filter_by(id=tag_id).first()
            if not item:
                abort(404, message="Item not found.")
            if not tag:
                abort(404, message="Tag not found.")
            if tag not in item.tags:
                item.tags.append(tag)
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message="Database error: {}".format(e))
        return item.tags, 201

    @blp.response(202, TagAndItemSchema)
    @blp.alt_response(404, description="Item or tag not found.")
    @blp.alt_response(500, description="Database error.")
    @jwt_required()
    def delete(self, item_id: int, tag_id: int) -> tuple[dict, int]:
        """Unlink a tag from an item

        Args:
            item_id (int): item id
            tag_id (int): tag id

        Returns:
            tuple[dict, int]: response message and status code
        """
        try:
            item = db.session.query(ItemModel).filter_by(id=item_id).first()
            tag = db.session.query(TagModel).filter_by(id=tag_id).first()
            if not item:
                abort(404, description="Item not found.")
            if not tag:
                abort(404, description="Tag not found.")
            if tag in item.tags:
                item.tags.remove(tag)
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message="Database error: {}".format(e))
        return { "message": "Tag unlinked" }, 202

@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    """ Tag resource """
    @blp.response(200, TagSchema)
    @blp.alt_response(404, description="Tag not found.")
    @jwt_required()
    def get(self, tag_id: int) -> tuple[dict, int]:
        """Get a tag

        Args:
            tag_id (int): tag id

        Returns:
            tuple[dict, int]: tag and status code
        """
        tag = db.session.query(TagModel).filter_by(id=tag_id).first()
        if not tag:
            abort(404, message="Tag not found.")
        return tag, 200

    @blp.response(202)
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(500, description="Database error.")
    @jwt_required()
    def delete(self, tag_id: int) -> tuple[dict, int]:
        """Delete a tag

        Args:
            tag_id (int): tag id

        Returns:
            tuple[dict, int]: response message and status code
        """
        try:
            tag = db.session.query(TagModel).filter_by(id=tag_id).first()
            if not tag:
                abort(404, message="Tag not found.")
            db.session.delete(tag)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            abort(500, message="Database error: {}".format(err))
        return { "message": "Tag deleted" }, 202
