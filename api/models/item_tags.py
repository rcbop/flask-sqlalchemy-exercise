"""Item tags model module."""
from api.db import db
from api.models.types import ItemTag

class ItemTags(db.Model): # type: ignore
    """Item tags model class."""
    __tablename__ = 'item_tags'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)


    def to_dict(self) -> ItemTag:
        """Converts item tag to dictionary.

        Returns:
            ItemTag: Item tag dictionary.
        """
        return {
            'id': self.id,
            'item_id': self.item_id,
            'tag_id': self.tag_id,
        }
