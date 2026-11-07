import os
os.environ.pop('DATABASE_URL',None)
from fastapi.testclient import TestClient
from app.main import app
def test_health_reports_configuration():
 r=TestClient(app).get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'; assert r.json()['version']=='1.1.0'


def test_local_frontend_origins_are_allowed():
 client=TestClient(app)
 for origin in ('http://localhost:5173','http://127.0.0.1:5173'):
  response=client.options('/api/v1/catalog/items',headers={'Origin':origin,'Access-Control-Request-Method':'GET'})
  assert response.status_code==200
  assert response.headers['access-control-allow-origin']==origin
