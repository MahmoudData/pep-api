import time
from pathlib import Path


def cleanup_file(file_path: Path, delay: int = 60):
    """Supprime le fichier après un délai"""
    time.sleep(delay)
    if file_path.exists():
        file_path.unlink()