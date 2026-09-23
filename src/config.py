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

GIF_EXTENSIONS = {
    ".gif",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mkv",
}

DEFAULT_INTERVAL = 0.2 * 60  # 2 minutos
RANDOM_MODE = True