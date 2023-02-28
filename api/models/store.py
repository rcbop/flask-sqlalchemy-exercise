""" Store model """
from api.db import db
from api.models.types import Store


class StoreModel(db.Model):  # type: ignore
    """Store model class."""

    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    items = db.relationship(
        "ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete"
    )
    tags = db.relationship(
        "TagModel", back_populates="store", lazy="dynamic", cascade="all, delete"
    )

    def to_dict(self) -> Store:
        """Converts store to dictionary.

        Returns:
            Store: Store dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "items": [item.to_dict() for item in list(self.items)],
            "tags": [tag.to_dict() for tag in list(self.tags)],
        }
