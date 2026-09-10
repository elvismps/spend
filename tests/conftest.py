import pytest
import database.db as db_module
from app import app as flask_app


@pytest.fixture
def app(tmp_path, monkeypatch):
    db_file = tmp_path / "test_spendly.db"
    monkeypatch.setattr(db_module, "DB_PATH", str(db_file))
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.app_context():
        db_module.init_db()
        db_module.seed_db()
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()
