import httpx
from .config import settings
BASE='https://api.github.com'
def headers():
    h={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
    if settings.github_token: h['Authorization']=f'Bearer {settings.github_token}'
    return h

def get_pr(owner,repo,number):
    with httpx.Client(timeout=20,headers=headers()) as c:
        pr=c.get(f'{BASE}/repos/{owner}/{repo}/pulls/{number}'); pr.raise_for_status()
        files=c.get(f'{BASE}/repos/{owner}/{repo}/pulls/{number}/files',params={'per_page':100}); files.raise_for_status()
        return pr.json(), files.json()
