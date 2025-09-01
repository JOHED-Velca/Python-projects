# Aule: Automated Job Application Bot

Aule is a Python-based bot designed to automate the process of applying to jobs. It streamlines job applications by handling tasks such as parsing job listings, filling out application forms, and managing application workflows, making the job search process more efficient and less time-consuming.

# Aule (Job Application Bot) — Step 1

Minimal runnable scaffold.

## Run (local)

First clear any process in progress otherwise it will crash (`sudo systemctl stop postgresql`)

1. `python -m venv .venv && source .venv/bin/activate` (or Windows equivalent)
2. `cp .env.example .env` and adjust values if needed
3. `pip install -r requirements.txt`
4. Ensure Postgres is running and `DATABASE_URL` is valid (or `docker compose up`)
5. `uvicorn app.main:app --reload`

Open http://localhost:8000

### Create a job

```bash
curl -X POST http://localhost:8000/jobs/ \
-H 'Content-Type: application/json' \
-d '{
"title": "Junior Software Developer",
"company": "NLS",
"location": "Toronto, ON",
"url": "https://example.com/job",
"description": "Junior Software Developer role...\n- Experience with Python\n- Knowledge of SQL and Docker\n- Good communication"
}'
```
