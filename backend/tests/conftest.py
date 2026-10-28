from pathlib import Path
import sys
import pytest
import json
import os
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.api import create_app
from app.config import Settings
from app.seed import seed, DEMO_PASSWORD
SURFACE_RESULTS=[]


@pytest.fixture(scope='session',autouse=True)
def write_surface_evidence():
    SURFACE_RESULTS.clear()
    yield
    location=os.getenv('SAMANVAY_EVIDENCE_DIR')
    if location and SURFACE_RESULTS:
        root=Path(__file__).resolve().parents[2]
        target=Path(location).resolve()
        if not target.is_relative_to((root/'docs/evidence').resolve()):raise RuntimeError('Evidence path must stay under docs/evidence')
        target.mkdir(parents=True,exist_ok=True)
        (target/'surface-matrix.json').write_text(json.dumps(SURFACE_RESULTS,indent=2)+'\n',encoding='utf-8')


@pytest.fixture
def system(tmp_path, monkeypatch):
    monkeypatch.setenv("SAMANVAY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SAMANVAY_ENV", "test")
    command.upgrade(Config(str(Path(__file__).parents[1] / "alembic.ini")), "head")
    settings = Settings(tmp_path, "test")
    app = create_app(settings)
    seed(settings, app.state.sessions)
    yield app
    app.state.engine.dispose()


@pytest.fixture
def client(system):
    with TestClient(system, raise_server_exceptions=False) as client:
        yield client


def signin(client, username="rb@demo.test"):
    response = client.post("/api/auth/login", json={"username": username, "password": DEMO_PASSWORD})
    assert response.status_code == 200, response.text
    return {"X-CSRF-Token": response.json()["csrf_token"]}
