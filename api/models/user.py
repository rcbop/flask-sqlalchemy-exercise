""" User model. """

from api.db import db
from api.models.types import User

class UserModel(db.Model): # type: ignore
    """ User model class. """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)

    def to_dict(self) -> User:
        """Converts user to dictionary.

        Returns:
            User: User dictionary.
        """
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email
        }
