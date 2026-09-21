from pathlib import Path

from src.config import SUPPORTED_EXTENSIONS


def scan_wallpapers(directories: list[Path]) -> list[Path]:
    wallpapers = []

    for directory in directories:
        if not directory.exists():
            continue

        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                wallpapers.append(path)

    return wallpapers