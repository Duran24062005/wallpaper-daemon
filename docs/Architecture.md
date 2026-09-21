Sí. Para la **V1 en Python**, mantendría los scripts pequeños y con una responsabilidad clara.

```text
wallpaper-manager/
├── src/
│   ├── main.py
│   ├── scanner.py
│   ├── wallpaper.py
│   ├── scheduler.py
│   └── config.py
├── tests/
│   ├── test_scanner.py
│   ├── test_wallpaper.py
│   └── test_config.py
├── pyproject.toml
└── README.md
```

### `config.py`

Responsable de la configuración:

```python
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
```

---

### `scanner.py`

Busca las imágenes disponibles.

```python
from pathlib import Path

from config import SUPPORTED_EXTENSIONS


def scan_wallpapers(directories: list[Path]) -> list[Path]:
    wallpapers = []

    for directory in directories:
        if not directory.exists():
            continue

        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                wallpapers.append(path)

    return wallpapers
```

---

### `wallpaper.py`

Se encarga exclusivamente de hablar con GNOME.

```python
import subprocess
from pathlib import Path


def set_wallpaper(image: Path) -> None:
    uri = image.resolve().as_uri()

    subprocess.run(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.background",
            "picture-uri",
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
```

---

### `scheduler.py`

Controla el cambio automático.

```python
import random
import time
from pathlib import Path

from wallpaper import set_wallpaper


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
```

La parte interesante aquí es:

```python
remaining.remove(wallpaper)
```

Así evitamos repetir una imagen hasta haber utilizado las demás.

---

### `main.py`

Es el punto de entrada y coordina los módulos.

```python
from config import (
    DEFAULT_INTERVAL,
    RANDOM_MODE,
    WALLPAPER_DIRECTORIES,
)
from scanner import scan_wallpapers
from scheduler import run_scheduler


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
```

---

## `tests/test_scanner.py`

Aquí podemos probar que el scanner encuentra correctamente las imágenes.

```python
from pathlib import Path

from src.scanner import scan_wallpapers


def test_scan_wallpapers(tmp_path: Path):
    (tmp_path / "wallpaper.jpg").touch()
    (tmp_path / "wallpaper.png").touch()
    (tmp_path / "document.txt").touch()

    wallpapers = scan_wallpapers([tmp_path])

    assert len(wallpapers) == 2
```

---

## `tests/test_config.py`

```python
from src.config import SUPPORTED_EXTENSIONS


def test_supported_extensions():
    assert ".jpg" in SUPPORTED_EXTENSIONS
    assert ".png" in SUPPORTED_EXTENSIONS
    assert ".webp" in SUPPORTED_EXTENSIONS
```

---

## `tests/test_wallpaper.py`

Aquí **no conviene cambiar realmente el wallpaper durante los tests**. Podemos hacer mocking posteriormente:

```python
from unittest.mock import patch
from pathlib import Path

from src.wallpaper import set_wallpaper


@patch("src.wallpaper.subprocess.run")
def test_set_wallpaper(mock_run, tmp_path: Path):
    image = tmp_path / "wallpaper.jpg"
    image.touch()

    set_wallpaper(image)

    mock_run.assert_called_once()
```

---

### `pyproject.toml`

Para empezar:

```toml
[project]
name = "wallpaper-manager"
version = "0.1.0"
description = "A lightweight Python wallpaper manager for Linux."
requires-python = ">=3.11"

[project.scripts]
wallpaper-manager = "src.main:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
]
```

Y como **no necesitamos ninguna dependencia externa para el MVP**, podemos mantenerlo prácticamente con la biblioteca estándar de Python.

La arquitectura inicial quedaría:

```text
                 main.py
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      config.py  scanner.py  scheduler.py
                    │            │
                    │            ▼
                    │       wallpaper.py
                    │            │
                    └────────────▼
                              GNOME
```

**Importante:** antes de escribir todo esto, yo haría primero un pequeño `main.py` experimental para verificar que `gsettings` funciona correctamente en tu Ubuntu. Una vez confirmado, construimos la arquitectura definitiva.
