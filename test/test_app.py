from api.app import create_app

def test_create_app():
    app = create_app()
    assert app is not None
    assert app.config["PROPAGATE_EXCEPTIONS"] is True
    assert app.config["API_TITLE"] == "Stores REST API"
    assert app.config["API_VERSION"] == "v1"
    assert app.config["OPENAPI_VERSION"] == "3.0.3"
    assert app.config["OPENAPI_URL_PREFIX"] == "/"
    assert app.config["OPENAPI_SWAGGER_UI_PATH"] == "/swagger-ui"
    assert app.config["OPENAPI_SWAGGER_UI_URL"] == "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///data.db"
    # assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False

def test_create_app_with_db_url():
    app = create_app("sqlite:///test.db")
    assert app is not None
    assert app.config["PROPAGATE_EXCEPTIONS"] is True
    assert app.config["API_TITLE"] == "Stores REST API"
    assert app.config["API_VERSION"] == "v1"
    assert app.config["OPENAPI_VERSION"] == "3.0.3"
    assert app.config["OPENAPI_URL_PREFIX"] == "/"
    assert app.config["OPENAPI_SWAGGER_UI_PATH"] == "/swagger-ui"
    assert app.config["OPENAPI_SWAGGER_UI_URL"] == "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///test.db"
