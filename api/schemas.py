""" serialization schemas for the api """
from marshmallow import Schema, fields


class PlainItemSchema(Schema):
    """ Item schema without store and tags """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainTagSchema(Schema):
    """ Tag schema without store and items """
    id = fields.Int(dump_only=True)
    name = fields.Str()

class PlainStoreSchema(Schema):
    """ Store schema without items and tags """
    id = fields.Int(dump_only=True)
    name = fields.Str()


class ItemSchema(PlainItemSchema):
    """ Item schema with store and tags """
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class ItemUpdateSchema(Schema):
    """ Item schema for updating an item """
    name = fields.Str()
    price = fields.Float()


class StoreSchema(PlainStoreSchema):
    """ Store schema with items and tags """
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    """ Tag schema with store and items """
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)

class TagAndItemSchema(Schema):
    """ Tag and Item schema for creating a tag and item """
    item = fields.Nested(PlainItemSchema())
    tag = fields.Nested(PlainTagSchema())

class UserSchema(Schema):
    """ User schema for login and registration """
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserRegisterSchema(UserSchema):
    """ User schema for registration """
    email = fields.Email(required=True)
