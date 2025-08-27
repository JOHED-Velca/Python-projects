from nlp import parser, scorer


def prefill_application(resume_text: str, job_description: str):
    jd = parser.parse_job_description(job_description)
    score = scorer.suitability_score(resume_text, job_description)
    bullets = [
        f"Experience matching: {', '.join(jd['requirements'][:3])}",
        f"Top skills to highlight: {', '.join(jd['skills'][:3])}",
    ]
    return {"summary": jd["summary"], "bullets": bullets, "score": score}