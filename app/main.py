from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from app.routes import preview, download, misc

app = FastAPI()

app.include_router(preview.router)
app.include_router(download.router)
app.include_router(misc.router)

@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.get("/health")
def health():
    return {"status": "ok"}