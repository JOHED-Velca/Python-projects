from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.sessions import SessionLocal
from db.models import Job
from worker.llm_client import LLMClient
from nlp import parser, scorer


router = APIRouter()


class TailorRequest(BaseModel):
job_id: int
resume_text: str


class TailorResponse(BaseModel):
cover_letter: str
suitability_score: float


@router.post("/cover-letter", response_model=TailorResponse)
def generate_cover_letter(body: TailorRequest):
db = SessionLocal()
try:
job = db.query(Job).get(body.job_id)
if not job:
raise HTTPException(404, "Job not found")


jd_struct = parser.parse_job_description(job.description)
score = scorer.suitability_score(body.resume_text, job.description)


prompt = (
f"You are a helpful assistant writing a one‑page cover letter.\n"
f"Job Title: {job.title}\nCompany: {job.company}\nLocation: {job.location or 'N/A'}\n"
f"Job Summary: {jd_struct['summary']}\nKey Requirements: {', '.join(jd_struct['requirements'])}\n\n"
f"Candidate Resume (raw):\n{body.resume_text}\n\n"
f"Write a concise, tailored cover letter in first person, professional but warm, using Canadian English."
)
llm = LLMClient()
letter = llm.complete(prompt)
return TailorResponse(cover_letter=letter, suitability_score=score)
finally:
db.close()