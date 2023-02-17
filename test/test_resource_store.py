from api.models import StoreModel

def test_get_store(test_client, db_fixture):
    store = StoreModel(name="Test Store")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    response = test_client.get(f'/store/{store.id}')
    assert response.status_code == 200

def test_get_store_not_found(test_client):
    response = test_client.get('/store/99')
    assert response.status_code == 404

def test_delete_store(test_client, db_fixture):
    store = StoreModel(name="Test Store 2")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    response = test_client.delete(f'/store/{store.id}')
    assert response.status_code == 202
    assert response.json == {"message": "Store deleted"}

def test_delete_store_not_found(test_client, db_fixture):
    response = test_client.delete('/store/99')
    assert response.status_code == 404

def test_get_stores(test_client, db_fixture):
    db_fixture.session.query(StoreModel).delete()
    store1 = StoreModel(name="Test Store 1")
    store2 = StoreModel(name="Test Store 2")
    db_fixture.session.add_all([store1, store2])
    db_fixture.session.commit()

    response = test_client.get('/store')
    assert response.status_code == 200
    assert len(response.json) == 2

def test_post_store(test_client):
    store_data = {'name': 'Test Store'}
    response = test_client.post('/store', json=store_data)
    assert response.status_code == 201

def test_post_store_duplicate_name(test_client, db_fixture):
    db_fixture.session.query(StoreModel).delete()
    store = StoreModel(name="Test Store")
    db_fixture.session.add(store)
    db_fixture.session.commit()

    store_data = {'name': 'Test Store'}
    response = test_client.post('/store', json=store_data)
    assert response.status_code == 409