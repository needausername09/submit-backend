from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
import zipfile
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== DATA MODEL ======
class Submission(BaseModel):
    student_name: str
    class_name: str
    code: str

BASE_DIR = "/tmp/submissions"
ZIP_PATH = "/tmp/all_submissions.zip"

os.makedirs(BASE_DIR, exist_ok=True)

# ====== SUBMIT ======
@app.post("/submit")
def submit_code(data: Submission):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{data.class_name}_{data.student_name}_{timestamp}.py"
    filepath = os.path.join(BASE_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(data.code)

    return {
        "status": "ok",
        "filename": filename
    }

# ====== DOWNLOAD ZIP ======
@app.get("/download")
def download_all():
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fname in os.listdir(BASE_DIR):
            zipf.write(
                os.path.join(BASE_DIR, fname),
                arcname=fname
            )

    return FileResponse(
        ZIP_PATH,
        media_type="application/zip",
        filename="all_submissions.zip"
    )
