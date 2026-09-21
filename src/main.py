from src.config import (
    DEFAULT_INTERVAL,
    RANDOM_MODE,
    WALLPAPER_DIRECTORIES,
)
from src.scanner import scan_wallpapers
from src.scheduler import run_scheduler


def main() -> None:
    print("Wallpaper Manager")
    print("-----------------")

    wallpapers = scan_wallpapers(WALLPAPER_DIRECTORIES)

    print(f"Found {len(wallpapers)} wallpapers.")

    if not wallpapers:
        print("No wallpapers found.")
        return

    run_scheduler(
        wallpapers=wallpapers,
        interval=DEFAULT_INTERVAL,
        random_mode=RANDOM_MODE,
    )


if __name__ == "__main__":
    main()