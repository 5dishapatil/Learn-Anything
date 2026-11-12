from __future__ import annotations

import os
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from app.config import BACKEND_DIR

_KEY_FILE = BACKEND_DIR / ".secret_key"
_cipher: Fernet | None = None


def _get_cipher() -> Fernet:
    global _cipher
    if _cipher is not None:
        return _cipher

    if _KEY_FILE.exists():
        try:
            key = _KEY_FILE.read_bytes().strip()
            _cipher = Fernet(key)
            return _cipher
        except Exception:
            pass

    # Generate new key and persist
    new_key = Fernet.generate_key()
    try:
        _KEY_FILE.write_bytes(new_key)
        # Attempt to restrict permissions on POSIX
        if os.name != "nt":
            try:
                os.chmod(_KEY_FILE, 0o600)
            except OSError:
                pass
    except Exception as exc:
        raise RuntimeError(f"Unable to persist encryption key: {exc}") from exc

    _cipher = Fernet(new_key)
    return _cipher


def encrypt_secret(plaintext: str | None) -> str:
    """Encrypt a secret string using Fernet symmetric encryption."""
    if not plaintext:
        return ""
    cipher = _get_cipher()
    encrypted_bytes = cipher.encrypt(plaintext.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_secret(ciphertext: str | None) -> str:
    """Decrypt a secret string. Fallback gracefully if legacy unencrypted plaintext."""
    if not ciphertext:
        return ""
    cipher = _get_cipher()
    try:
        decrypted_bytes = cipher.decrypt(ciphertext.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except (InvalidToken, ValueError):
        # Legacy unencrypted plaintext fallback for seamless backward compatibility
        return ciphertext


def mask_secret(secret: str | None) -> str:
    """Mask a secret string for safe display in UI/API responses."""
    if not secret:
        return ""
    decrypted = decrypt_secret(secret)
    if not decrypted:
        return ""
    if len(decrypted) <= 4:
        return "••••"
    return f"••••••••{decrypted[-4:]}"
