# test_core.py
from core_stego import prepare_payload, apply_ecc
import os
import base64

def test():
    print("=== TEST START ===")

    # Step 1: Fake file to hide
    filename = "secret.txt"
    content = b"THIS IS A SECRET TEXT THAT WILL BE HIDDEN INSIDE VIDEO FRAMES!!!"

    # Step 2: Password
    password = "mypassword123"

    # Step 3: Prepare payload (compress + encrypt)
    encrypted_blob = prepare_payload(content, filename, password)
    print(f"[+] Encrypted Payload Size: {len(encrypted_blob)} bytes")

    # Step 4: ECC wrap
    ecc_blob = apply_ecc(encrypted_blob)
    print(f"[+] ECC Added Size: {len(ecc_blob)} bytes")

    # Step 5: Show first 64 bytes as preview
    print("[+] Payload Preview (base64 first 64 chars):")
    print(base64.b64encode(ecc_blob)[:64])

    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    test()

