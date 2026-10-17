"""Explicit downloads of version 1 task bundles from Google's model storage."""

import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import urlretrieve

MODELS = {
    "face_landmarker": "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff",
    "gesture_recognizer": "97952348cf6a6a4915c2ea1496b4b37ebabc50cbbf80571435643c455f2b0482",
}


def download_models(directory: Path):
    """Verify SHA-256 before replacing a bundle; interrupted downloads are removed."""
    directory.mkdir(parents=True, exist_ok=True)
    for name, expected in MODELS.items():
        target = directory / f"{name}.task"
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == expected:
            continue
        url = f"https://storage.googleapis.com/mediapipe-models/{name}/{name}/float16/1/{name}.task"
        with NamedTemporaryFile(dir=directory, suffix=".part", delete=False) as handle:
            partial = Path(handle.name)
        try:
            urlretrieve(url, partial)
            if hashlib.sha256(partial.read_bytes()).hexdigest() != expected:
                raise ValueError(f"Model checksum failed for {name}")
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)
