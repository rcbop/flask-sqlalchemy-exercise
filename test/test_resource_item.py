from api.models import ItemModel
from api.schemas import ItemSchema


def test_get_item(test_client, db_fixture, auth_header):
    item = ItemModel(name="test item", price=9.99, store_id=1)
    db_fixture.session.add(item)
    db_fixture.session.commit()

    response = test_client.get(f"/item/{item.id}", headers=auth_header)

    assert response.status_code == 200
    assert response.json == ItemSchema().dump(item)


def test_delete_item(test_client, db_fixture, auth_header):
    item = ItemModel(name="test item", price=9.99, store_id=1)
    db_fixture.session.add(item)
    db_fixture.session.commit()

    response = test_client.delete(f"/item/{item.id}", headers=auth_header)

    assert response.status_code == 202
    assert response.json == {"message": "Item deleted."}
    assert db_fixture.session.query(ItemModel).filter_by(id=item.id).first() is None


def test_put_item(test_client, db_fixture, auth_header):
    item = ItemModel(name="test item", price=9.99, store_id=1)
    db_fixture.session.add(item)
    db_fixture.session.commit()

    updated_data = {"name": "updated item", "price": 12.99}
    response = test_client.put(
        f"/item/{item.id}", json=updated_data, headers=auth_header
    )

    assert response.status_code == 200
    updated_item = db_fixture.session.query(ItemModel).filter_by(id=item.id).first()
    assert updated_item.name == updated_data["name"]
    assert updated_item.price == updated_data["price"]


def test_get_item_list(test_client, db_fixture, auth_header):
    db_fixture.session.query(ItemModel).delete()
    item1 = ItemModel(name="item 1", price=9.99, store_id=1)
    item2 = ItemModel(name="item 2", price=12.99, store_id=1)
    db_fixture.session.add_all([item1, item2])
    db_fixture.session.commit()

    response = test_client.get("/item", headers=auth_header)

    assert response.status_code == 200
    expected_data = ItemSchema(many=True).dump([item1, item2])
    assert response.json == expected_data


def test_post_item(test_client, auth_header):
    new_item_data = {"name": "new item", "price": 14.99, "store_id": 1}

    response = test_client.post("/item", json=new_item_data, headers=auth_header)

    assert response.status_code == 201
    new_item = ItemModel.query.filter_by(name=new_item_data["name"]).first()
    assert new_item is not None
    assert response.json == ItemSchema().dump(new_item)
