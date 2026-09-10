import json, subprocess, sys
from pathlib import Path

def scan_path(path: str) -> list[dict]:
    cmd=[sys.executable,"-m","bandit","-r",path,"-f","json","-q"]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    # Bandit returns nonzero when findings exist.
    raw=proc.stdout.strip()
    if not raw:
        if proc.stderr.strip(): raise RuntimeError(proc.stderr.strip())
        return []
    data=json.loads(raw)
    findings=[]
    for r in data.get("results",[]):
        findings.append({
          "tool":"bandit","rule_id":r.get("test_id","B000"),"severity":r.get("issue_severity","LOW"),
          "confidence":r.get("issue_confidence"),"filename":r.get("filename","").replace(str(Path(path)),".",1),
          "line":r.get("line_number",0),"message":r.get("issue_text","")
        })
    return findings
