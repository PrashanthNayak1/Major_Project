# video_encode.py

import os
from typing import List
import cv2
import numpy as np
from PIL import Image
import subprocess

from core_stego import prepare_payload, embed_bytes_into_frames
from backend.progress_state import PROGRESS

  

def extract_frames(video_path: str) -> List[Image.Image]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video")

    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(rgb))

    cap.release()
    print(f"[+] Extracted {len(frames)} frames")
    return frames


def rebuild_video_with_audio(frames, output_path, fps, orig_video_path):
    """
    1) Build stego video WITHOUT audio (FFV1 lossless codec)
    2) Merge original audio using ffmpeg WITHOUT re-encoding
    """
    temp_no_audio = output_path.replace(".mkv", "_noaudio.mkv")
    w, h = frames[0].size

    # ---- STEP 1: Write frames (no audio yet)
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter(temp_no_audio, fourcc, fps, (w, h))

    total_frames = len(frames)
    for i, frame in enumerate(frames):
        bgr = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        out.write(bgr)

        # ---- REAL PROGRESS UPDATE  (Video Writing)
        PROGRESS["encode"] = 50 + int((i / total_frames) * 50)  # 50–100%

    out.release()

    print("[+] Video without audio created")

    # ---- STEP 2: Merge original audio
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_no_audio,
        "-i", orig_video_path,
        "-c:v", "copy",   # do NOT re-encode video
        "-c:a", "copy",   # keep original audio
        output_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(temp_no_audio)

    print("[+] Merged original audio successfully!")


def encode_video(video_path, file_path, password, out_path="encoded.mkv"):
    # Reset progress at start
    PROGRESS["encode"] = 0

    hidden_bytes = open(file_path, "rb").read()
    payload = prepare_payload(hidden_bytes, os.path.basename(file_path), password)

    # ---- Frame Extraction Stage
    frames = extract_frames(video_path)
    total_frames = len(frames)
    fps = cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FPS) or 30

    # ---- Embedding Stage (0–50% progress)
    stego_frames = []
    for i, frame in enumerate(embed_bytes_into_frames(frames, payload)):
        stego_frames.append(frame)
        PROGRESS["encode"] = int((i / total_frames) * 50)   # 0–50%

    # ---- Rebuild Video + Add Audio (50–100%)
    rebuild_video_with_audio(stego_frames, out_path, fps=fps, orig_video_path=video_path)

    PROGRESS["encode"] = 100
    print("[✔] Encoding Complete with audio preserved!")
