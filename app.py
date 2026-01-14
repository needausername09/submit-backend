from fastapi import FastAPI
from pydantic import BaseModel
import subprocess, tempfile

app = FastAPI()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # cho phép mọi frontend (ok cho nội bộ)
    allow_credentials=True,
    allow_methods=["*"],          # cho phép POST, OPTIONS, v.v.
    allow_headers=["*"],
)

class Code(BaseModel):
    code: str

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
    return {"output": result.stdout + result.stderr}
