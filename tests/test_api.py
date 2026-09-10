from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get('/health').status_code==200
def test_inline_scan_detects_eval():
    r=client.post('/scan/code',json={'filename':'x.py','code':'user="1+1"\nprint(eval(user))'})
    assert r.status_code==200
    assert any(f['rule_id']=='EXEC001' for f in r.json()['findings'])
