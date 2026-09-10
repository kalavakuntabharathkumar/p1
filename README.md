# AI-Powered Security & Code Review Automation for REST APIs

FastAPI service that scans Python repositories/code with Bandit + custom AST heuristics, stores findings, optionally uses OpenAI/Claude for severity triage, and creates reviewer-focused GitHub PR summaries.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
uvicorn app.main:app --reload --port 8001
```

Open `http://localhost:8001/docs`.

## Endpoints

- `POST /scan/code` — scan pasted Python using Bandit + AST heuristics.
- `POST /scan/repository` — clone a public GitHub `owner/repo` and scan it.
- `POST /pr/summary` — retrieve PR metadata/files from GitHub and produce a summary.
- `GET /scans/{id}` — retrieve persisted scan results.
- `GET /health`

Without an AI key, triage and PR summaries use a deterministic local fallback, so the project is still demoable. To use AI, set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, `AI_PROVIDER`, and a compatible `AI_MODEL`.

## Evaluation / resume-metric workflow

The supplied description's numbers (12 repositories, 37 findings, 9 SQLi risks, 25 PRs, 71% review-time reduction, false-positive rate reduction) should be **reproduced from real runs**, not hard-coded. Use:

```bash
python scripts/benchmark_review_time.py --before 14 13 15 --after 4 5 3
python scripts/evaluate_alerts.py labeled_alerts.csv
```

For a defensible portfolio write-up, save the exact repository list/commit SHAs, Bandit JSON, manually labeled ground truth, and before/after PR review timings.

## Security notes

Repository scans only construct HTTPS GitHub URLs from validated `owner`/`repo` fields; they do not accept arbitrary shell commands. Cloning and Bandit execution use argument arrays rather than `shell=True`.
