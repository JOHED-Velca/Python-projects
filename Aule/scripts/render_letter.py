from db.sessions import SessionLocal
from db.models import Job
from pdf.render import render_cover_letter
from pathlib import Path

db = SessionLocal()
job = db.query(Job).get(1)
db.close()
if not job:
    raise SystemExit("No job with id=1. Create one via POST /jobs/ first.")

context = {
    "job_title": job.title,
    "company": job.company,
    "location": job.location,
    "summary": "Highly motivated developer with experience aligning with your requirements.",
    "requirements": ["Python", "SQL", "Docker"],
    "intro": "I am excited to apply for this role at your company.",
    "closing": "Thank you for your time and consideration."
}

html = render_cover_letter(context)
out = Path("/app/out"); out.mkdir(exist_ok=True)
(out / "cover_letter.html").write_text(html, encoding="utf-8")
print("Wrote /app/out/cover_letter.html")
