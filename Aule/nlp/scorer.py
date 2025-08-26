from nlp.embeddings import embed, cosine


def suitability_score(resume_text: str, job_text: str) -> float:
# cosine similarity of mock embeddings → [0, 1]
sim = cosine(embed(resume_text), embed(job_text))
return round(max(0.0, min(1.0, (sim + 1) / 2)), 4)