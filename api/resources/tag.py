from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from api.db import db
from api.models import TagModel, StoreModel, ItemModel
from api.schemas import TagSchema, TagAndItemSchema

blp = Blueprint('Tags', 'tags', description='Operations on tags')

@blp.route("/stores/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = db.session.query(StoreModel).filter_by(id=store_id).first()
        if not store:
            abort(404, message="Store not found.")
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, new_tag, store_id):
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
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message="Database error: {}".format(e))
        return tag, 201

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema(many=True))
    def post(self, item_id, tag_id):
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
    def delete(self, item_id, tag_id):
        try:
            item = db.session.query(ItemModel).filter_by(id=item_id).first()
            tag = db.session.query(TagModel).filter_by(id=tag_id).first()
            if not item:
                abort(404, message="Item not found.")
            if not tag:
                abort(404, message="Tag not found.")
            if tag in item.tags:
                item.tags.remove(tag)
                db.session.commit()
            return { "message": "Tag unlinked" }, 202
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message="Database error: {}".format(e))

@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = db.session.query(TagModel).filter_by(id=tag_id).first()
        if not tag:
            abort(404, message="Tag not found.")
        return tag

    @blp.response(202)
    def delete(self, tag_id):
        try:
            tag = db.session.query(TagModel).filter_by(id=tag_id).first()
            if not tag:
                abort(404, message="Tag not found.")
            db.session.delete(tag)
            db.session.commit()
            return { "message": "Tag deleted" }, 202
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message="Database error: {}".format(e))