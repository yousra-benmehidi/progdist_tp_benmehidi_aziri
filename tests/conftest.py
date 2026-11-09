import pytest

from tp_1 import db
from tp_1.app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Each test gets its own brand-new database file, deleted afterwards.
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    return app.test_client()
