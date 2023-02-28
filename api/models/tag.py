""" Tag model. """

from api.db import db
from api.models.types import Tag


class TagModel(db.Model):  # type: ignore
    """Tag model class."""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    store = db.relationship("StoreModel", back_populates="tags")
    items = db.relationship("ItemModel", secondary="item_tags", back_populates="tags")

    def to_dict(self) -> Tag:
        """Converts tag to dictionary.

        Returns:
            Tag: Tag dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "store_id": self.store_id,
            "store": self.store.to_dict(),
            "items": [item.to_dict() for item in list(self.items)],
        }
