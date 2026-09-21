import subprocess
from pathlib import Path


def set_wallpaper(image: Path) -> None:
    uri = image.resolve().as_uri()

    for key in ("picture-uri", "picture-uri-dark"):
        subprocess.run(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.background",
                key,
                uri,
            ],
            check=True,
        )


def get_current_wallpaper() -> str:
    result = subprocess.run(
        [
            "gsettings",
            "get",
            "org.gnome.desktop.background",
            "picture-uri",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()