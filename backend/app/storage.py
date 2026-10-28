from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import secrets
from fastapi import HTTPException

MAX_FILE = 5 * 1024 * 1024
MAX_FILES = 3


@dataclass
class Evidence:
    filename: str
    content: bytes
    detected_type: str
    sha256: str


async def prepare_files(files):
    if len(files) > MAX_FILES:
        raise HTTPException(422, "Upload at most three evidence files.")
    prepared = []
    for file in files:
        content = await file.read(MAX_FILE + 1)
        if not content or len(content) > MAX_FILE:
            raise HTTPException(422, "Each evidence file must be nonempty and no larger than 5 MiB.")
        filename = re.split(r"[/\\]", file.filename or "evidence")[-1]
        filename = "".join(c for c in filename if c.isprintable())[:150]
        extension = Path(filename).suffix.lower()
        valid = False
        if extension == ".pdf":
            valid, detected = content.startswith(b"%PDF-"), "application/pdf"
        elif extension == ".png":
            valid, detected = content.startswith(b"\x89PNG\r\n\x1a\n"), "image/png"
        elif extension in {".jpg", ".jpeg"}:
            valid, detected = content.startswith(b"\xff\xd8\xff") and content.endswith(b"\xff\xd9"), "image/jpeg"
        elif extension == ".txt":
            detected = "text/plain"
            try:
                text = content.decode("utf-8")
                valid = not any(ord(c) < 32 and c not in "\n\r\t" for c in text)
            except UnicodeDecodeError:
                valid = False
        else:
            detected = "application/octet-stream"
        if not valid:
            raise HTTPException(422, "Evidence must be a matching PDF, PNG, JPEG or UTF-8 TXT file. Browser MIME is not trusted.")
        prepared.append(Evidence(filename, content, detected, hashlib.sha256(content).hexdigest()))
    return prepared


def private_path(settings, storage_key):
    if not re.fullmatch(r"[a-f0-9]{48}\.bin", storage_key):
        raise ValueError("Invalid private storage key")
    base = settings.attachments_dir.resolve()
    path = (base / storage_key).resolve()
    if not path.is_relative_to(base):
        raise ValueError("Invalid private storage location")
    return path


def store(settings, evidence):
    settings.attachments_dir.mkdir(parents=True, exist_ok=True)
    key = secrets.token_hex(24) + ".bin"
    path = private_path(settings, key)
    temporary = path.with_suffix(".staging")
    try:
        with temporary.open("xb") as stream:
            stream.write(evidence.content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return key, path
