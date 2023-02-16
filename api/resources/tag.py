from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from api.db import db
from api.models import TagModel, StoreModel
from api.schemas import TagSchema

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
