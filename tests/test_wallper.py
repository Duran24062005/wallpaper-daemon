from unittest.mock import patch
from pathlib import Path

from src.wallpaper import set_wallpaper


@patch("src.wallpaper.subprocess.run")
def test_set_wallpaper(mock_run, tmp_path: Path):
    image = tmp_path / "wallpaper.jpg"
    image.touch()

    set_wallpaper(image)

    mock_run.assert_called_once()