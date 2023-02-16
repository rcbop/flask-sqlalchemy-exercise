import pytest
from api.app import create_app
from api.db import db
from api.models import ItemModel, TagModel, StoreModel

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
def db_fixture(app_fixture):
    with app_fixture.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture
def tag():
    tag = TagModel(name="Test tag")
    db_fixture.session.add(tag)
    db_fixture.session.commit()
    return tag

def test_link_tag_to_item(test_client, db_fixture):
    store = StoreModel(name="Test Store")
    db_fixture.session.add(store)
    db_fixture.session.commit()
    item = ItemModel(name="Test item", price=10.99, store_id=store.id)
    tag1 = TagModel(name="Test tag 1", store_id=store.id)
    item.tags.append(tag1)
    db_fixture.session.add(item)
    db_fixture.session.commit()
    response = test_client.post(f"/item/{item.id}/tag/{tag1.id}")
    assert response.status_code == 201
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Test tag 1"

def test_unlink_tag_from_item(test_client, db_fixture):
    store = StoreModel(name="Test Store 1")
    db_fixture.session.add(store)
    db_fixture.session.commit()
    item = ItemModel(name="Test item 1", price=10.99, store_id=store.id)
    tag1 = TagModel(name="Test tag 2", store_id=store.id)
    item.tags.append(tag1)
    db_fixture.session.add(item)
    db_fixture.session.commit()
    response = test_client.delete(f"/item/{item.id}/tag/{tag1.id}")
    assert response.status_code == 202

def test_link_tag_to_item_not_found(test_client, db_fixture):
    response = test_client.post("/item/99/tag/1")
    assert response.status_code == 404

def test_link_tag_to_item_tag_not_found(test_client, db_fixture):
    store = StoreModel(name="Test Store 2")
    db_fixture.session.add(store)
    db_fixture.session.commit()
    item = ItemModel(name="Test item 2", price=10.99, store_id=store.id)
    db_fixture.session.add(item)
    db_fixture.session.commit()
    response = test_client.post(f"/item/{item.id}/tag/99")
    assert response.status_code == 404

def test_unlink_tag_from_item_not_found(test_client, db_fixture):
    response = test_client.delete("/item/99/tag/1")
    assert response.status_code == 404