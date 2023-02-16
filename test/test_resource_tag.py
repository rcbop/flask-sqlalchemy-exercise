import pytest

from api.app import create_app
from api.db import db
from api.models import TagModel, StoreModel

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

def test_get_tags_in_store(test_client, db_fixture):
    # add a store and some tags to it
    store = StoreModel(name="Test Store 1")
    db_fixture.session.add(store)
    db_fixture.session.commit()
    tags = [
        TagModel(name="Tag 1", store_id=store.id),
        TagModel(name="Tag 2", store_id=store.id),
        TagModel(name="Tag 3", store_id=store.id),
    ]
    db_fixture.session.add_all(tags)
    db_fixture.session.commit()

    response = test_client.get(f"/stores/{store.id}/tag")
    assert response.status_code == 200
    assert len(response.json) == 3
    assert response.json[0]["name"] == "Tag 1"
    assert response.json[1]["name"] == "Tag 2"
    assert response.json[2]["name"] == "Tag 3"

def test_add_tag_to_store(test_client, db_fixture):
    # add a store to the database
    store = StoreModel(name="Test Store 2")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    # create a new tag to add to the store
    new_tag = {"name": "New Tag"}

    # test adding the new tag to the store
    response = test_client.post(f"/stores/{store.id}/tag", json=new_tag)
    assert response.status_code == 201

    # make sure the tag was added to the database
    tag = TagModel.query.filter_by(name=new_tag["name"], store_id=store.id).first()
    assert tag is not None
    assert tag.name == new_tag["name"]
    assert tag.store_id == store.id

def test_add_tag_to_nonexistent_store(test_client, db_fixture):
    # add a store to the database
    store = StoreModel(name="Test Store 3")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    # create a new tag to add to the store
    new_tag = {"name": "New Tag"}

    # test adding the new tag to the store
    response = test_client.post(f"/stores/{store.id + 1}/tag", json=new_tag)
    assert response.status_code == 404

def test_get_tags_in_nonexistent_store(test_client, db_fixture):
    # add a store to the database
    store = StoreModel(name="Test Store 4")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    # test getting the tags from the store
    response = test_client.get(f"/stores/{store.id + 1}/tag")
    assert response.status_code == 404

def test_add_tag_with_duplicate_name_to_store(test_client, db_fixture):
    # add a store to the database
    store = StoreModel(name="Test Store 5")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    # create a new tag to add to the store
    new_tag = {"name": "New Tag"}

    # test adding the new tag to the store
    response = test_client.post(f"/stores/{store.id}/tag", json=new_tag)
    assert response.status_code == 201

    # test adding the new tag to the store again
    response = test_client.post(f"/stores/{store.id}/tag", json=new_tag)
    assert response.status_code == 409

def test_add_tag_without_name_to_store(test_client, db_fixture):
    # add a store to the database
    store = StoreModel(name="Test Store 6")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    # create a new tag to add to the store
    new_tag = {}

    # test adding the new tag to the store
    response = test_client.post(f"/stores/{store.id}/tag", json=new_tag)
    assert response.status_code == 400