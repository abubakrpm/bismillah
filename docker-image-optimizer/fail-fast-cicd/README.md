# Fail-Fast CI/CD Pipeline

A small Flask task API with a GitHub Actions pipeline built on one principle: **fail fast, fail cheap.** Stages run from cheapest to most expensive, so a lint error fails in seconds instead of after a 10-minute build.

## Pipeline

```
lint ──┬── unit-tests ──┬── build ── image-scan ── integration ── deploy-staging ── deploy-production
       └── security ────┘                                                         (manual approval)
```

| Stage | What it does | Fails on |
|---|---|---|
| `lint` | Ruff lint + format check | Style or obvious code errors |
| `unit-tests` | pytest with Flask test client (no container) | Broken logic |
| `security` | gitleaks secret scan + bandit SAST | Leaked keys, insecure code (medium+) |
| `build` | Docker Buildx with GitHub Actions layer cache | Build errors |
| `image-scan` | Trivy | HIGH/CRITICAL CVEs that have a fix |
| `integration` | Runs the real container, tests it over HTTP | Container doesn't start or behave |
| `deploy-staging` | Pushes image to GHCR, deploys (main only) | |
| `deploy-production` | Deploys after approval | |

Design choices:

- `unit-tests` and `security` run **in parallel** since neither depends on the other.
- Security checks are **blocking**, not just warnings.
- `concurrency` cancels outdated runs when you push again.
- The image is built **once** and reused by every later stage, so what you test is exactly what you ship.
- Pip and Docker layers are **cached** between runs.
- Every job has a `timeout-minutes` so a hung job can't block the pipeline for hours.

## Project structure

```
fail-fast-cicd/
├── .github/workflows/pipeline.yml
├── app/main.py                 # Flask API: /health, /tasks
├── tests/
│   ├── test_unit.py            # Fast, in-process
│   └── test_integration.py     # Against the running container (needs APP_URL)
├── Dockerfile                  # Slim, non-root, gunicorn
├── requirements.txt
├── requirements-dev.txt
└── ruff.toml
```

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

ruff check . && ruff format --check .
bandit -r app/ --severity-level medium
pytest tests/test_unit.py -v

# Integration tests against a real container
docker build -t task-api .
docker run -d -p 8000:8000 --name task-api task-api
APP_URL=http://localhost:8000 pytest tests/test_integration.py -v
```

## Set it up on GitHub

1. Push this folder to a new GitHub repo.
2. Go to **Settings → Environments** and create `staging` and `production`.
3. On `production`, add yourself under **Required reviewers**. That turns the last stage into a manual gate.
4. Push to `main` and watch the **Actions** tab.

## Demo the fail-fast behavior

Try breaking things on a branch and opening a PR:

- Add an unused import → fails at `lint` within seconds, nothing else runs.
- Change an assertion in `test_unit.py` → fails at `unit-tests`, build never starts.
- Add `subprocess.run(request.args["cmd"], shell=True)` to a route in `main.py` → `security` blocks it (bandit B602, command injection).
- Swap the base image to an old one like `python:3.8` → `image-scan` blocks it.
