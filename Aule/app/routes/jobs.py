from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from db.sessions import SessionLocal
from db import models


router = APIRouter()


class JobCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    url: Optional[str] = None
    description: str = Field(..., min_length=20)


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str]
    url: Optional[str]
    description: str


class Config:
    from_attributes = True


@router.post("/", response_model=JobOut)
def create_job(payload: JobCreate):
    db = SessionLocal()
    try:
        job = models.Job(
            title=payload.title,
            company=payload.company,
            location=payload.location,
            url=payload.url,
            description=payload.description,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


@router.get("/", response_model=List[JobOut])
def list_jobs():
    db = SessionLocal()
    try:
        jobs = db.query(models.Job).order_by(models.Job.id.desc()).all()
        return jobs
    finally:
        db.close()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(models.Job).get(job_id)
        if not job:
            raise HTTPException(404, "Job not found")
            return job
    finally:
        db.close()