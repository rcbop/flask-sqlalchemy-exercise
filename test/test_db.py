from api import db

def test_db():
    assert db.db is not None