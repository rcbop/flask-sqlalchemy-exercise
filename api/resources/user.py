from collections import namedtuple

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_

from api.auth.blocklist import BLOCKLIST
from api.db import db
from api.models import UserModel
from api.schemas import UserRegisterSchema, UserSchema
from api.email import send_email_from_postmaster

blp = Blueprint("Users", "users", description="Operations on users")

# trying with namedtuples
UserData = namedtuple('UserData', ['username', 'password', 'email'])


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201)
    @blp.alt_response(409, description="Username already exists")
    def post(self, user_data):
        # experimenting with namedtuples
        user_data = UserData(**user_data)
        if db.session.query(UserModel).filter(
                or_(
                    UserModel.username == user_data.username,
                    UserModel.email == user_data.email
                )
            ).first():
            abort(409, message="Username already exists")

        try:
            user = UserModel(
                username=user_data.username,
                password=pbkdf2_sha256.hash(user_data.password),
                email=user_data.email
            )
            db.session.add(user)
            db.session.commit()

            current_app.queue.enqueue(
                send_email_from_postmaster,
                mail_to=user_data.username,
                subject="Successful registration",
                body=f"Welcome {user.username}! You have successfully registered to our Stores API."
            )
        except:
            abort(500, message="Internal server error")
        return {"message": "User registered!"}, 201


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    @blp.alt_response(404, description="User not found")
    def get(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found")
        return user

    @blp.response(202)
    @blp.alt_response(404, description="User not found")
    @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted!"}, 202

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = db.session.query(UserModel).filter_by(username=user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
        return {"message": "Invalid credentials"}, 401

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": access_token}, 200
