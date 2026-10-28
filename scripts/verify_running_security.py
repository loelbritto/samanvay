"""Local API/proxy exposure smoke check; never prints cookie/password/private bytes."""
import hashlib
import json
from pathlib import Path
import sqlite3
import httpx

ROOT=Path(__file__).resolve().parents[1]


def main():
    rows=[]
    with httpx.Client(base_url='http://127.0.0.1:8000',timeout=15) as client:
        for url in ['/api/cases','/api/reports/csv','/api/notifications','/api/relationships','/api/transfers']:
            r=client.get(url);assert r.status_code==401
            assert r.headers['x-content-type-options']=='nosniff' and r.headers['cache-control']=='no-store'
            rows.append({'surface':url,'status':r.status_code,'passed':True})
        blocked=client.post('/api/auth/login',headers={'Origin':'https://untrusted.example'},json={'username':'rb@demo.test','password':'DemoOnly-Stage2!'})
        assert blocked.status_code==403
        login=client.post('/api/auth/login',json={'username':'rb@demo.test','password':'DemoOnly-Stage2!'})
        assert login.status_code==200
        record=client.get('/api/cases/DEMO-20BF09829C05').json()
        attachment=record['attachments'][0]
        download=client.get(attachment['download_url']);assert download.status_code==200
        assert hashlib.sha256(download.content).hexdigest()==attachment['sha256']
    with httpx.Client(base_url='http://127.0.0.1:5173',timeout=15) as frontend:
        for path in [ROOT/'.local-data/samanvay.sqlite3',ROOT/'backend/app/config.py']:
            assert path.is_file()
            url='/@fs/'+path.as_posix()
            r=frontend.head(url);assert r.status_code in {403,404},(str(path),r.status_code)
            rows.append({'surface':'Vite private-path HEAD '+path.relative_to(ROOT).as_posix(),'status':r.status_code,'passed':True})
        assert frontend.get('/api/cases').status_code==401
    with sqlite3.connect('file:'+(ROOT/'.local-data/samanvay.sqlite3').as_posix()+'?mode=ro',uri=True) as db:
        cases=db.execute('SELECT public_id FROM cases ORDER BY public_id').fetchall()
        assert {c[0] for c in cases}=={'PGRC-014','PGRC-019','RB-023','RB-031','DEMO-20BF09829C05'}
        audit_count=db.execute('SELECT count(*) FROM security_audit').fetchone()[0]
        assert audit_count>0
    report={'passed':True,'checks':rows,'wrong_origin_login_status':403,'preserved_case_count':len(cases),
        'attachment_checksum_verified':True,'significant_access_records_present':True,'external_integration':'none'}
    output=ROOT/'docs/evidence/stage7/running-security.json'
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()
