from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import tempfile

app = FastAPI()

# CORS (bắt buộc cho Netlify / browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Code(BaseModel):
    code: str

# Route test backend sống
@app.get("/")
def root():
    return {"status": "backend is running"}

# Route chạy code
@app.post("/run")
def run_code(data: Code):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(data.code)
        fname = f.name

    result = subprocess.run(
        ["python", fname],
        capture_output=True,
        text=True,
        timeout=3
    )

    return {
        "output": result.stdout + result.stderr
    }
