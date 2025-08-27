from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import jobs as jobs_router
from app.routes import tailor as tailor_router


app = FastAPI(title="Aule Job Bot", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(jobs_router.router, prefix="/jobs", tags=["jobs"])
app.include_router(tailor_router.router, prefix="/tailor", tags=["tailor"])


@app.get("/")
def health():
    return {"ok": True, "service": "Aule", "version": "0.1.0"}