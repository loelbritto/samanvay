"""Small startup smoke run in the newly installed Python environment/data directory."""
import importlib.metadata
import json
from fastapi.testclient import TestClient
from app.api import create_app

app=create_app()
with TestClient(app) as client:
    assert client.get('/api/health').status_code==200
    assert client.get('/api/cases').status_code==401
    login=client.post('/api/auth/login',json={'username':'rb@demo.test','password':'DemoOnly-Stage2!'})
    assert login.status_code==200
    assert client.get('/api/overview').json()['total']==1
    assert client.get('/api/cases/RB-023').json()['original_submission']
app.state.engine.dispose()
print(json.dumps({'passed':True,'scope':'Fresh Python dependency installation, migrated/add-only-seeded isolated data, startup/sign-in/scoped original read',
    'versions':{name:importlib.metadata.version(name) for name in ['fastapi','SQLAlchemy','alembic','argon2-cffi','httpx']}}))
