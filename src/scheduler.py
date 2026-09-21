import random
import time
from pathlib import Path

from src.wallpaper import set_wallpaper


def run_scheduler(
    wallpapers: list[Path],
    interval: int,
    random_mode: bool = True,
) -> None:
    if not wallpapers:
        raise ValueError("No wallpapers found.")

    remaining = wallpapers.copy()

    while True:
        if not remaining:
            remaining = wallpapers.copy()

        if random_mode:
            wallpaper = random.choice(remaining)
            remaining.remove(wallpaper)
        else:
            wallpaper = remaining.pop(0)

        print(f"Changing wallpaper: {wallpaper}")

        set_wallpaper(wallpaper)

        print(f"Next change in {interval} seconds.")

        time.sleep(interval)