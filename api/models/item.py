"""Item model module."""
from api.db import db
from api.models.types import Item


class ItemModel(db.Model):  # type: ignore
    """Item model class."""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    description = db.Column(db.String)

    store_id = db.Column(
        db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False
    )
    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagModel", secondary="item_tags", back_populates="items")

    def to_dict(self) -> Item:
        """Converts item to dictionary.

        Returns:
            Item: Item dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "store_id": self.store_id,
            "tags": [tag.to_dict() for tag in list(self.tags)],
        }
