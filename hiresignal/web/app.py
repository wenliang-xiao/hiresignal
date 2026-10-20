"""HireSignal Web 服务（FastAPI）。"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..services.search import SearchService

app = FastAPI(title="HireSignal · 融资雷达")
svc = SearchService()

STATIC_DIR = Path(__file__).parent / "static"


class AskReq(BaseModel):
    question: str


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
def status():
    return {"providers": [{"id": p.id, "ready": True} for p in svc.providers]}


@app.get("/api/search")
def search(q: str):
    return {"results": svc.search(q)}


@app.get("/api/company")
def company(name: str):
    detail = svc.company_detail(name)
    return {"company": detail}


@app.post("/api/ask")
def ask(req: AskReq):
    return {"answer": svc.ask(req.question)}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
