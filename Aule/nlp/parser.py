import re
from typing import Dict, List


def parse_job_description(text: str) -> Dict[str, List[str] | str]:
# ultra-simple heuristics for step 1
lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
summary = lines[0] if lines else "No summary found"
# naive requirement extraction by bullets or keywords
reqs = [ln for ln in lines if ln.startswith(("- ", "• ", "* "))]
if not reqs:
reqs = [ln for ln in lines if re.search(r"experience|required|responsibilities|skills", ln, re.I)]
# naive skills extraction
skills = re.findall(r"\b(Python|Java|C\+\+|TypeScript|SQL|Docker|Kubernetes|AWS|GCP|Azure|React|FastAPI|Django|Rust|ML|NLP)\b", text, re.I)
skills = list(dict.fromkeys([s.capitalize() for s in skills]))
return {
"summary": summary[:280],
"requirements": reqs[:10],
"skills": skills[:15],
}