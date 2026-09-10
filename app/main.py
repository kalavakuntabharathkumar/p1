import json, os, subprocess, tempfile
from pathlib import Path
import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .ai import summarize_pr, triage_findings
from .bandit_scan import scan_path
from .config import settings
from .db import Base, engine, get_db
from .github_client import get_pr
from .heuristics import scan_python
from .models import Scan
from .schemas import CodeScanRequest, PRSummaryRequest, RepoScanRequest, ScanResponse

if settings.sentry_dsn: sentry_sdk.init(dsn=settings.sentry_dsn,traces_sample_rate=0.2)
Base.metadata.create_all(bind=engine)
app=FastAPI(title='AI Security & Code Review Automation',version='1.0.0')

def dedupe(findings):
    seen=set(); out=[]
    for f in findings:
        k=(f['rule_id'],f['filename'],f['line'],f['message'])
        if k not in seen: seen.add(k); out.append(f)
    return out

def counts(findings):
    c={'HIGH':0,'MEDIUM':0,'LOW':0}
    for f in findings: c[f['severity'].upper()]=c.get(f['severity'].upper(),0)+1
    return c

def save_scan(db, repo, findings, summary=''):
    row=Scan(repo=repo,findings_json=json.dumps(findings),summary=summary); db.add(row); db.commit(); db.refresh(row); return row.id

@app.get('/health')
def health(): return {'status':'ok','ai_configured':bool(settings.openai_api_key or settings.anthropic_api_key)}

@app.post('/scan/code',response_model=ScanResponse)
def scan_code(req: CodeScanRequest, db: Session=Depends(get_db)):
    suffix='.py' if not req.filename.endswith('.py') else ''
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/(req.filename+suffix); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(req.code,encoding='utf-8')
        findings=dedupe(scan_python(req.filename,req.code)+scan_path(td))
    triage=triage_findings(findings); sid=save_scan(db,'inline',findings,triage)
    return {'scan_id':sid,'repo':'inline','findings':findings,'counts':counts(findings),'ai_triage':triage}

@app.post('/scan/repository',response_model=ScanResponse)
def scan_repo(req: RepoScanRequest, db: Session=Depends(get_db)):
    repo_url=f'https://github.com/{req.owner}/{req.repo}.git'
    with tempfile.TemporaryDirectory() as td:
        try:
            subprocess.run(['git','clone','--depth','1',repo_url,td],check=True,capture_output=True,text=True,timeout=90)
        except Exception as e: raise HTTPException(400,f'Could not clone repository: {e}')
        findings=scan_path(td)
        for p in Path(td).rglob('*.py'):
            try: findings.extend(scan_python(str(p.relative_to(td)),p.read_text(encoding='utf-8',errors='ignore')))
            except Exception: pass
    findings=dedupe(findings); triage=triage_findings(findings); name=f'{req.owner}/{req.repo}'; sid=save_scan(db,name,findings,triage)
    return {'scan_id':sid,'repo':name,'findings':findings,'counts':counts(findings),'ai_triage':triage}

@app.post('/pr/summary')
def pr_summary(req: PRSummaryRequest):
    try: pr,files=get_pr(req.owner,req.repo,req.pull_number)
    except Exception as e: raise HTTPException(400,f'GitHub API error: {e}')
    return {'repository':f'{req.owner}/{req.repo}','pull_number':req.pull_number,'summary':summarize_pr(pr.get('title',''),pr.get('body') or '',files),'files_changed':len(files)}

@app.get('/scans/{scan_id}')
def get_scan(scan_id:int,db:Session=Depends(get_db)):
    row=db.get(Scan,scan_id)
    if not row: raise HTTPException(404,'Scan not found')
    return {'id':row.id,'repo':row.repo,'created_at':row.created_at,'findings':json.loads(row.findings_json),'summary':row.summary}
