import pytest

from api.app import create_app
from api.db import db
from api.models import ItemModel
from api.schemas import ItemSchema

@pytest.fixture(scope="module")
def app_fixture():
    app = create_app("sqlite:///:memory:")
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture(scope="module")
def test_client(app_fixture):
    with app_fixture.test_client() as client:
        yield client

@pytest.fixture(scope="module")
def db_session(app_fixture):
    with app_fixture.app_context():
        db.create_all()
        yield db.session
        db.drop_all()


def test_get_item(test_client, db_session):
    # create an item
    item = ItemModel(name="test item", price=9.99, store_id=1)
    db_session.add(item)
    db_session.commit()

    # make GET request to retrieve the item
    response = test_client.get(f'/item/{item.id}')

    # assert the response code and data
    assert response.status_code == 200
    assert response.json == ItemSchema().dump(item)


def test_delete_item(test_client, db_session):
    # create an item
    item = ItemModel(name="test item", price=9.99, store_id=1)
    db_session.add(item)
    db_session.commit()

    # make DELETE request to delete the item
    response = test_client.delete(f'/item/{item.id}')

    # assert the response code and message
    assert response.status_code == 200
    assert response.json == {"message": "Item deleted."}

    # check that the item no longer exists in the database
    assert db_session.query(ItemModel).filter_by(id=item.id).first() is None


def test_put_item(test_client, db_session):
    # create an item
    item = ItemModel(name="test item", price=9.99, store_id=1)
    db_session.add(item)
    db_session.commit()

    # update the item
    updated_data = {"name": "updated item", "price": 12.99}
    response = test_client.put(f'/item/{item.id}', json=updated_data)

    # assert the response code and data
    assert response.status_code == 200
    updated_item = db_session.query(ItemModel).filter_by(id=item.id).first()
    assert updated_item.name == updated_data["name"]
    assert updated_item.price == updated_data["price"]


def test_get_item_list(test_client, db_session):
    # create some items
    db_session.query(ItemModel).delete()
    item1 = ItemModel(name="item 1", price=9.99, store_id=1)
    item2 = ItemModel(name="item 2", price=12.99, store_id=1)
    db_session.add_all([item1, item2])
    db_session.commit()

    # make GET request to retrieve the list of items
    response = test_client.get('/item')

    # assert the response code and data
    assert response.status_code == 200
    expected_data = ItemSchema(many=True).dump([item1, item2])
    assert response.json == expected_data


def test_post_item(test_client, db_session):
    # create new item data
    new_item_data = {"name": "new item", "price": 14.99, "store_id": 1}

    # make POST request to create new item
    response = test_client.post('/item', json=new_item_data)

    # assert the response code and data
    assert response.status_code == 201
    new_item = ItemModel.query.filter_by(name=new_item_data["name"]).first()
    assert new_item is not None
    assert response.json == ItemSchema().dump(new_item)
