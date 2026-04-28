import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
import config

def _hex_to_bytes(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)

def _parse_key_info(secret: str):
    if not secret or ":" not in secret:
        return None
    parts = secret.split(":")
    if len(parts) != 2:
        return None
    try:
        return {
            "key": _hex_to_bytes(parts[0]),
            "iv": _hex_to_bytes(parts[1])
        }
    except ValueError:
        return None

KEYS = {}
if config.CRICIFY_PROVIDER_SECRET1:
    k1 = _parse_key_info(config.CRICIFY_PROVIDER_SECRET1)
    if k1: KEYS["key1"] = k1

if config.CRICIFY_PROVIDER_SECRET2:
    k2 = _parse_key_info(config.CRICIFY_PROVIDER_SECRET2)
    if k2: KEYS["key2"] = k2

def decrypt_data(encrypted_base64: str) -> str:
    """
    Decrypts base64 encoded AES-CBC encrypted data.
    """
    if not KEYS:
        print("Warning: No crypto keys configured.")
        return None

    try:
        clean_base64 = encrypted_base64.strip().replace("\n", "").replace("\r", "").replace(" ", "").replace("\t", "")
        ciphertext = base64.b64decode(clean_base64)

        for key_name, key_info in KEYS.items():
            result = _try_decrypt(ciphertext, key_info)
            if result:
                return result
        return None
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def _try_decrypt(ciphertext: bytes, key_info: dict) -> str:
    try:
        cipher = AES.new(key_info["key"], AES.MODE_CBC, key_info["iv"])
        decrypted_padded = cipher.decrypt(ciphertext)
        decrypted = unpad(decrypted_padded, AES.block_size)
        text = decrypted.decode('utf-8')
        
        # Validate result looks like JSON or contains http
        if text.startswith("{") or text.startswith("[") or "http" in text.lower():
            return text
        return None
    except Exception:
        return None
