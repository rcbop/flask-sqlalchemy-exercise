from api.models import TagModel, StoreModel

def test_get_tag_without_store(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    new_tag = {"name": "New Tag"}

    tag = TagModel(**new_tag, store_id=store.id)
    db_fixture.session.add(tag)
    db_fixture.session.commit()

    response = test_client.get("/tag/1", headers=auth_header)
    assert response.status_code == 200
    assert response.json["name"] == "New Tag"

def test_get_tag_without_store_not_found(test_client, auth_header):
    response = test_client.get("/tag/99", headers=auth_header)
    assert response.status_code == 404

def test_delete_tag_without_store(test_client, auth_header):
    response = test_client.delete("/tag/1", headers=auth_header)
    assert response.status_code == 202

def test_delete_tag_without_store_not_found(test_client, auth_header):
    response = test_client.delete("/tag/99", headers=auth_header)
    assert response.status_code == 404


def test_get_tags_in_store(test_client, db_fixture, auth_header):
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

    response = test_client.get(f"/stores/{store.id}/tag", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json) == 3
    assert response.json[0]["name"] == "Tag 1"
    assert response.json[1]["name"] == "Tag 2"
    assert response.json[2]["name"] == "Tag 3"

def test_add_tag_to_store(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store 2")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    new_tag = {"name": "New Tag"}

    response = test_client.post(f"/stores/{store.id}/tag", json=new_tag, headers=auth_header)
    assert response.status_code == 201

    tag = TagModel.query.filter_by(name=new_tag["name"], store_id=store.id).first()
    assert tag is not None
    assert tag.name == new_tag["name"]
    assert tag.store_id == store.id

def test_add_tag_to_nonexistent_store(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store 3")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    new_tag = {"name": "New Tag"}

    response = test_client.post(f"/stores/{store.id + 1}/tag", json=new_tag, headers=auth_header)
    assert response.status_code == 404

def test_get_tags_in_nonexistent_store(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store 4")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    response = test_client.get(f"/stores/{store.id + 1}/tag", headers=auth_header)
    assert response.status_code == 404

def test_add_tag_with_duplicate_name_to_store(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store 5")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    new_tag = {"name": "New Tag"}

    response = test_client.post(f"/stores/{store.id}/tag", json=new_tag, headers=auth_header)
    assert response.status_code == 201
    response = test_client.post(f"/stores/{store.id}/tag", json=new_tag, headers=auth_header)
    assert response.status_code == 409

def test_add_tag_without_name_to_store(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store 6")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    new_tag = {}

    response = test_client.post(f"/stores/{store.id}/tag", json=new_tag, headers=auth_header)
    assert response.status_code == 400