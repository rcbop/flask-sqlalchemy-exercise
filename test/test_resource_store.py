from api.models import StoreModel

def test_get_store(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    response = test_client.get(f'/store/{store.id}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['name'] == "Test Store"
    db_fixture.session.query(StoreModel).count() == 1
    db_fixture.session.query(StoreModel).delete()

def test_get_store_not_found(test_client, auth_header):
    response = test_client.get('/store/99', headers=auth_header)
    assert response.status_code == 404

def test_delete_store(test_client, db_fixture, auth_header):
    store = StoreModel(name="Test Store 2")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    response = test_client.delete(f'/store/{store.id}', headers=auth_header)
    assert response.status_code == 202
    assert response.json == {"message": "Store deleted"}
    db_fixture.session.query(StoreModel).count() == 0

def test_delete_store_not_found(test_client, db_fixture, auth_header):
    response = test_client.delete('/store/99', headers=auth_header)
    assert response.status_code == 404

def test_get_stores(test_client, db_fixture, auth_header):
    db_fixture.session.query(StoreModel).delete()
    store1 = StoreModel(name="Test Store 1")
    store2 = StoreModel(name="Test Store 2")
    db_fixture.session.add_all([store1, store2])
    db_fixture.session.commit()

    response = test_client.get('/store', headers=auth_header)
    assert response.status_code == 200
    assert len(response.json) == 2

def test_post_store(test_client, db_fixture, auth_header):
    store_data = {'name': 'Test Store'}
    response = test_client.post('/store', json=store_data, headers=auth_header)
    assert response.status_code == 201
    assert response.json['name'] == "Test Store"
    db_fixture.session.query(StoreModel).count() == 1
    db_fixture.session.query(StoreModel).delete()

def test_post_store_duplicate_name(test_client, db_fixture, auth_header):
    db_fixture.session.query(StoreModel).delete()
    store = StoreModel(name="Test Store")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    store_data = {'name': 'Test Store'}
    response = test_client.post('/store', json=store_data, headers=auth_header)
    assert response.status_code == 409