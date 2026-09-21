from pathlib import Path

WALLPAPER_DIRECTORIES = [
    Path.home() / ".local/share/backgrounds",
]

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

DEFAULT_INTERVAL = 1 * 60  # 2 minutos
RANDOM_MODE = True