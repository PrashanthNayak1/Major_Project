import os
import zlib
import cv2
from PIL import Image

from core_stego import extract_bytes_from_frames, derive_key, aes_gcm_decrypt
from backend.progress_state import PROGRESS    



def decode_video(video_path: str, password: str, out_dir: str = "recovered"):
    PROGRESS["decode"] = 0

    os.makedirs(out_dir, exist_ok=True)
    tmp_file = os.path.join(out_dir, "payload.tmp")

    frames = []
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        PROGRESS["decode"] = int((idx / total) * 30)  # 0-30%
        idx += 1

    cap.release()

    payload_path = extract_bytes_from_frames(frames, tmp_file)
    PROGRESS["decode"] = 60  # payload extracted

    blob = open(payload_path, "rb").read()

    MAGIC = b"VSTEG1"
    if not blob.startswith(MAGIC):
        raise ValueError("Invalid stego video or wrong password")

    i = len(MAGIC)
    name_len = blob[i]; i += 1
    filename = blob[i:i+name_len].decode("utf-8"); i += name_len

    i += 8  # skip original size

    salt = blob[i:i+16]; i += 16
    nonce = blob[i:i+12]; i += 12
    tag = blob[i:i+16]; i += 16
    ct = blob[i:]

    PROGRESS["decode"] = 80  # decrypting

    key = derive_key(password, salt)
    data = zlib.decompress(aes_gcm_decrypt(key, nonce, ct, tag))

    out_path = os.path.join(out_dir, filename)
    open(out_path, "wb").write(data)

    PROGRESS["decode"] = 100
    print("[✔] File recovered:", out_path)

    return out_path
