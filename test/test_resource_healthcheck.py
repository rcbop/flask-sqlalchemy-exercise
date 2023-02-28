def test_healthcheck(test_client):
    response = test_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json["message"] == "OK"
