from api.models import ItemModel, StoreModel, TagModel


def test_link_tag_to_item(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store")
    db_fixture.session.add(store)
    db_fixture.session.commit()
    item = ItemModel(name="Test item", price=10.99, store_id=store.id)
    tag1 = TagModel(name="Test tag 1", store_id=store.id)
    item.tags.append(tag1)
    db_fixture.session.add(item)
    db_fixture.session.commit()
    response = test_client.post(f"/item/{item.id}/tag/{tag1.id}", headers=auth_header)
    assert response.status_code == 201
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Test tag 1"


def test_unlink_tag_from_item(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store 1")
    db_fixture.session.add(store)
    db_fixture.session.commit()
    item = ItemModel(name="Test item 1", price=10.99, store_id=store.id)
    tag1 = TagModel(name="Test tag 2", store_id=store.id)
    item.tags.append(tag1)
    db_fixture.session.add(item)
    db_fixture.session.commit()
    response = test_client.delete(f"/item/{item.id}/tag/{tag1.id}", headers=auth_header)
    assert response.status_code == 202


def test_link_tag_to_item_not_found(test_client, auth_header):
    response = test_client.post("/item/99/tag/1", headers=auth_header)
    assert response.status_code == 404


def test_link_tag_to_item_tag_not_found(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store 2")
    db_fixture.session.add(store)
    db_fixture.session.commit()
    item = ItemModel(name="Test item 2", price=10.99, store_id=store.id)
    db_fixture.session.add(item)
    db_fixture.session.commit()
    response = test_client.post(f"/item/{item.id}/tag/99", headers=auth_header)
    assert response.status_code == 404


def test_unlink_tag_from_item_not_found(test_client, auth_header):
    response = test_client.delete("/item/99/tag/1", headers=auth_header)
    assert response.status_code == 404
