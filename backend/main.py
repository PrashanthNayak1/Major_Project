import os
import shutil
import tempfile
from pathlib import Path
import mimetypes
import sys

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from progress_state import PROGRESS

PROGRESS = {"encode": 0, "decode": 0}


# Allow imports of core python files
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from video_encode import encode_video
from video_decode import decode_video

app = FastAPI(title="Video Steganography API")

# CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def save_upload_to_temp(upload: UploadFile, suffix: str) -> str:
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    with open(tmp_path, "wb") as out_f:
        shutil.copyfileobj(upload.file, out_f)
    upload.file.close()
    return tmp_path

@app.get("/")
async def root():
    return {"status": "ok", "message": "Video Steganography API running"}

# ======================================================
# ENCODE
# ======================================================
@app.post("/encode")
async def encode(
    video: UploadFile = File(...),
    file: UploadFile = File(...),
    password: str = Form(...),
):
    if not password:
        raise HTTPException(status_code=400, detail="Password required")

    video_suffix = Path(video.filename).suffix or ".mkv"
    file_suffix = Path(file.filename).suffix or ".bin"

    cover_video = save_upload_to_temp(video, video_suffix)
    secret_file = save_upload_to_temp(file, file_suffix)

    fd, stego_output = tempfile.mkstemp(suffix=".mkv")
    os.close(fd)

    try:
        encode_video(cover_video, secret_file, password, stego_output)
    except Exception as e:
        for p in [cover_video, secret_file, stego_output]:
            if os.path.exists(p):
                os.remove(p)
        raise HTTPException(status_code=500, detail=str(e))

    if os.path.exists(cover_video): os.remove(cover_video)
    if os.path.exists(secret_file): os.remove(secret_file)

    return Response(
        content=open(stego_output, "rb").read(),
        media_type="video/x-matroska",
        headers={
            "Content-Disposition": f'attachment; filename="stego_{Path(video.filename).stem}.mkv"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )

# ======================================================
# DECODE
# ======================================================
@app.post("/decode")
async def decode(
    stego_video: UploadFile = File(...),
    password: str = Form(...)
):
    if not password:
        raise HTTPException(status_code=400, detail="Password required")

    suffix = Path(stego_video.filename).suffix or ".mkv"
    stego_temp = save_upload_to_temp(stego_video, suffix)
    out_dir = tempfile.mkdtemp()

    try:
        recovered_path = decode_video(stego_temp, password, out_dir)
    except Exception as e:
        if os.path.exists(stego_temp): os.remove(stego_temp)
        shutil.rmtree(out_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

    if os.path.exists(stego_temp): os.remove(stego_temp)

    filename = os.path.basename(recovered_path)
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    data = open(recovered_path, "rb").read()

    return Response(
        content=data,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
@app.get("/progress/encode")
async def encode_progress():
    return {"progress": PROGRESS["encode"]}

@app.get("/progress/decode")
async def decode_progress():
    return {"progress": PROGRESS["decode"]}

