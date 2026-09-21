from pathlib import Path

from src.scanner import scan_wallpapers


def test_scan_wallpapers(tmp_path: Path):
    (tmp_path / "wallpaper.jpg").touch()
    (tmp_path / "wallpaper.png").touch()
    (tmp_path / "document.txt").touch()

    wallpapers = scan_wallpapers([tmp_path])

    assert len(wallpapers) == 2