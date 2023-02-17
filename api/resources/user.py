from collections import namedtuple

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256

from api.db import db
from api.models import UserModel
from api.schemas import UserSchema

blp = Blueprint("Users", "users", description="Operations on users")

# trying with namedtuples
UserData = namedtuple('UserData', ['username', 'password'])


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201)
    @blp.alt_response(409, description="Username already exists")
    @blp.alt_response(400, description="Missing username or password")
    def post(self, user_data):
        if "username" not in user_data or "password" not in user_data:
            abort(409, message="Missing username or password")

        # experimenting with namedtuples
        user_data = UserData(**user_data)
        if UserModel.query.filter_by(username=user_data.username).first():
            abort(409, message="Username already exists")
        user = UserModel(
            username=user_data.username,
            password=pbkdf2_sha256.hash(user_data.password)
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered!"}, 201

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    @blp.alt_response(404, description="User not found")
    def get(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found")
        return user

    @blp.response(202)
    @blp.alt_response(404, description="User not found")
    def delete(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted!"}, 202