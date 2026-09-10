from .config import settings

def _fallback(findings: list[dict]) -> str:
    high=sum(1 for f in findings if f['severity'].upper()=='HIGH')
    medium=sum(1 for f in findings if f['severity'].upper()=='MEDIUM')
    return f"Local triage: {high} high and {medium} medium severity findings. Review high-severity items first; validate data flow before marking exploitable."

def triage_findings(findings: list[dict]) -> str:
    if not findings: return "No findings to triage."
    prompt="Triage these security findings. Remove likely duplicates/false positives, prioritize exploitable issues, and give concise remediation. Findings: "+str(findings[:80])
    if settings.ai_provider.lower()=="openai" and settings.openai_api_key:
        from openai import OpenAI
        client=OpenAI(api_key=settings.openai_api_key)
        r=client.responses.create(model=settings.ai_model,input=prompt)
        return r.output_text
    if settings.ai_provider.lower()=="anthropic" and settings.anthropic_api_key:
        import anthropic
        client=anthropic.Anthropic(api_key=settings.anthropic_api_key)
        r=client.messages.create(model=settings.ai_model,max_tokens=900,messages=[{"role":"user","content":prompt}])
        return ''.join(b.text for b in r.content if hasattr(b,'text'))
    return _fallback(findings)

def summarize_pr(title: str, body: str, files: list[dict]) -> str:
    changes='\n'.join(f"- {f.get('filename')}: +{f.get('additions',0)} -{f.get('deletions',0)}" for f in files[:50])
    prompt=f"Write a reviewer-focused PR summary with: purpose, key changes, risk areas, test checklist. Title: {title}\nBody: {body}\nFiles:\n{changes}"
    if settings.ai_provider.lower()=="openai" and settings.openai_api_key:
        from openai import OpenAI
        return OpenAI(api_key=settings.openai_api_key).responses.create(model=settings.ai_model,input=prompt).output_text
    return f"PR: {title}\n\nKey changed files:\n{changes}\n\nReview focus: authentication/authorization, input validation, database calls, secrets, and changed tests."
