from pathlib import Path

WALLPAPER_DIRECTORIES = [
    Path.home() / "Pictures",
]

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

DEFAULT_INTERVAL = 30 * 60  # 30 minutos
RANDOM_MODE = True