#core_stego.py
import os
import zlib
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from typing import Tuple, List 
from PIL import Image         
import numpy as np    

MAGIC = b"VSTEG1"
SALT_LEN = 16
KEY_LEN = 32
NONCE_LEN = 12
TAG_LEN = 16
PBKDF2_ITERS = 200_000



# ---- KEY & CRYPTO ----
def derive_key(password: str, salt: bytes) -> bytes:
    return PBKDF2(
        password.encode(),
        salt,
        dkLen=KEY_LEN,
        count=PBKDF2_ITERS,
        hmac_hash_module=SHA256,
    )


def aes_gcm_encrypt(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    nonce = os.urandom(NONCE_LEN)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(data)
    return nonce, tag, ct


def aes_gcm_decrypt(key: bytes, nonce: bytes, ct: bytes, tag: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ct, tag)


# ---- PAYLOAD PREPARATION (FILE -> COMPRESS -> ENCRYPT -> BLOB) ----
def prepare_payload(file_bytes: bytes, filename: str, password: str) -> bytes:
    """
    Creates payload:
      MAGIC || 1 byte fname_len || fname || 8 byte file_size ||
      salt || nonce || tag || ciphertext
    """

    # ---- compress first ----
    compressed = zlib.compress(file_bytes)
    file_size = len(file_bytes)

    # ---- derive key ----
    salt = os.urandom(SALT_LEN)
    key = derive_key(password, salt)

    # ---- encrypt compressed data ----
    nonce, tag, ct = aes_gcm_encrypt(key, compressed)

    # ---- filename handling ----
    fname_bytes = filename.encode("utf-8")
    fname_len = len(fname_bytes)
    if fname_len > 255:
        fname_bytes = fname_bytes[:255]  # truncate
        fname_len = 255

    # ---- build payload ----
    header = bytearray()
    header += MAGIC                      # 6 bytes
    header += fname_len.to_bytes(1, "big")
    header += fname_bytes
    header += file_size.to_bytes(8, "big")
    header += salt
    header += nonce
    header += tag

    return bytes(header) + ct



# ---- ECC (DISABLED FOR NOW – JUST PASSTHROUGH) ----
def apply_ecc(blob: bytes) -> bytes:
    """
    Placeholder ECC function.
    Right now it simply returns the data unchanged so encode/decode stay consistent.

    If you later want real ECC:
      - encode side:  ecc_blob = RS.encode(blob)
      - decode side:  blob = RS.decode(ecc_blob)
    """
    return blob


# ---- BIT CONVERSION ----
def _bytes_to_bits(data: bytes):
    bits = []
    for b in data:
        for i in range(8):
            bits.append((b >> (7 - i)) & 1)
    return bits


def _bits_to_bytes(bits: list) -> bytes:
    if len(bits) % 8 != 0:
        bits = bits[: len(bits) - (len(bits) % 8)]
    out = bytearray()
    for i in range(0, len(bits), 8):
        val = 0
        for bit in bits[i : i + 8]:
            val = (val << 1) | (bit & 1)
        out.append(val)
    return bytes(out)


# ---- EMBED BYTES INTO FRAMES (LSB) ----
def embed_bytes_into_frames(frames: List[Image.Image], data: bytes) -> List[Image.Image]:
    """
    frames : list of PIL.Image (RGB)
    data   : bytes to hide

    We add a 4-byte length prefix and then embed all bits into LSBs
    of all frames in order.
    """
    # 4-byte big-endian length prefix
    length_bytes = len(data).to_bytes(4, "big")
    payload = length_bytes + data
    bits = _bytes_to_bits(payload)

    total_bits_needed = len(bits)
    total_capacity = sum(f.size[0] * f.size[1] * 3 for f in frames)
    if total_bits_needed > total_capacity:
        raise ValueError(
            f"Not enough capacity: need {total_bits_needed} bits, have {total_capacity} bits."
        )

    out_frames: List[Image.Image] = []
    bit_index = 0

    for frame in frames:
        if bit_index >= total_bits_needed:
            # no more bits to embed, just copy as-is
            out_frames.append(frame.copy())
            continue

        arr = np.array(frame.convert("RGB"), dtype=np.uint8)
        flat = arr.reshape(-1)

        for i in range(flat.size):
            if bit_index >= total_bits_needed:
                break
            bit = bits[bit_index]
            # set LSB safely
            flat[i] = (flat[i] & 0xFE) | bit
            bit_index += 1

        out_frames.append(Image.fromarray(flat.reshape(arr.shape), "RGB"))

    return out_frames


# ---- INTERNAL: STREAM BITS FROM FRAMES ----
def _iter_frame_bits(frames: List[Image.Image]):
    """Yield LSBs from frames ONE BY ONE (no big list in RAM)."""
    for frame in frames:
        arr = np.array(frame.convert("RGB"), dtype=np.uint8)
        flat = arr.reshape(-1)
        for val in flat:
            yield (val & 1)


# ---- EXTRACT BYTES FROM FRAMES (STREAM TO DISK) ----
def extract_bytes_from_frames(frames: List[Image.Image], tmp_path: str = "payload.tmp") -> str:
    """
    Reads bits from frames, reconstructs the payload and writes it to tmp_path.

    Returns: path to the written payload file (string).
    """
    bit_stream = _iter_frame_bits(frames)

    # --- read 32-bit payload length ---
    length_bits = [next(bit_stream) for _ in range(32)]
    data_len = int.from_bytes(_bits_to_bytes(length_bits), "big")
    total_bits = data_len * 8

    print(f"[+] Payload Size: {data_len} bytes ({total_bits} bits)")

    # --- stream bits into a temp file ---
    with open(tmp_path, "wb") as f:
        byte_val = 0
        bit_count = 0

        for _ in range(total_bits):
            bit = next(bit_stream)
            # keep as plain Python int, 0–255
            byte_val = ((byte_val << 1) | bit) & 0xFF
            bit_count += 1

            if bit_count == 8:
                f.write(int(byte_val).to_bytes(1, "big"))
                byte_val = 0
                bit_count = 0

    print("[✔] Raw payload saved on disk:", tmp_path)
    return tmp_path
