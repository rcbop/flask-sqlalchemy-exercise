""" Type definitions for models. """
from typing import TypedDict

class User(TypedDict):
    """ User type definition. """
    id: int
    username: str
    password: str
    email: str

class Tag(TypedDict):
    """ Tag type definition. """
    id: int
    name: str
    store_id: int
    items: list['ItemTag']


class Item(TypedDict):
    """ Item type definition."""
    id: int
    name: str
    price: float
    description: str
    store_id: int
    tags: list['ItemTag']


class Store(TypedDict):
    """ Store type definition. """
    id: int
    name: str
    items: list[Item]
    tags: list[Tag]


class ItemTag(TypedDict):
    """Item tag type definition."""
    id: int
    item_id: int
    tag_id: int
