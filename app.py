from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import subprocess
import tempfile
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

# ====== MODELS ======
class Code(BaseModel):
    code: str

class Submission(BaseModel):
    student_name: str
    class_name: str
    code: str

BASE_DIR = "/tmp/submissions"
ZIP_PATH = "/tmp/all_submissions.zip"
os.makedirs(BASE_DIR, exist_ok=True)

# ====== RUN CODE (KHÔNG LƯU FILE) ======
@app.post("/run")
def run_code(data: Code):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(data.code)
        fname = f.name

    try:
        result = subprocess.run(
            ["python", fname],
            capture_output=True,
            text=True,
            timeout=3
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        output = "❌ Code chạy quá thời gian cho phép (3s)"
    finally:
        os.remove(fname)

    return {"output": output}

# ====== SUBMIT (LƯU FILE .py) ======
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
