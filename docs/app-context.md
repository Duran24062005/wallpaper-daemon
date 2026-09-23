# App Context

Sí. Revisé directamente el repositorio actual de [wallpaper-daemon en GitHub](https://github.com/Duran24062005/wallpaper-daemon?utm_source=chatgpt.com), y hay algo importante que entender:

> **Python realmente no está modificando el fondo de pantalla directamente. Python está actuando como intermediario entre tu programa y GNOME.**

La cadena actual es:

```text
Python
  │
  │ subprocess.run()
  ▼
gsettings
  │
  │ modifica una configuración de GNOME
  ▼
GNOME Desktop
  │
  ▼
Wallpaper
```

Y sí: **es técnicamente posible hacer que cada monitor tenga un wallpaper diferente**, pero tu implementación actual no lo hace. Para conseguirlo habría que cambiar la estrategia de integración con GNOME.

---

# 1. ¿Qué hace realmente tu código?

La parte fundamental está en:

```python
src/wallpaper.py
```

Actualmente tienes:

```python
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
```

Esta función parece sencilla, pero tiene varias capas interesantes.

---

# 2. Primero conviertes el archivo en una URI

Esta línea:

```python
uri = image.resolve().as_uri()
```

supongamos que tienes:

```text
/home/alexi/.local/share/backgrounds/montana.jpg
```

`Path.resolve()` obtiene la ruta absoluta:

```text
/home/alexi/.local/share/backgrounds/montana.jpg
```

y:

```python
.as_uri()
```

la transforma en:

```text
file:///home/alexi/.local/share/backgrounds/montana.jpg
```

¿Por qué?

Porque GNOME no está recibiendo simplemente:

```text
/home/alexi/...
```

sino una **URI de archivo**.

---

# 3. Aquí ocurre la verdadera interacción con el sistema

La parte más importante es:

```python
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
```

Python está ejecutando literalmente un comando del sistema.

Es equivalente a que tú abrieras una terminal y escribieras:

```bash
gsettings set org.gnome.desktop.background picture-uri file:///home/alexi/.local/share/backgrounds/montana.jpg
```

Python simplemente está haciendo eso automáticamente.

---

# 4. ¿Qué es `gsettings`?

`gsettings` es una herramienta de Linux/GNOME para consultar y modificar configuraciones almacenadas mediante **GSettings**.

Puedes probarlo tú mismo:

```bash
gsettings get org.gnome.desktop.background picture-uri
```

Probablemente obtendrás algo parecido a:

```text
'file:///home/alexi/.local/share/backgrounds/wallpaper.jpg'
```

Y puedes modificarlo:

```bash
gsettings set org.gnome.desktop.background picture-uri file:///ruta/imagen.jpg
```

Por tanto:

```text
Python
   ↓
subprocess
   ↓
gsettings
   ↓
GSettings
   ↓
GNOME
   ↓
Desktop background
```

---

# 5. ¿Y por qué funciona sin `sudo`?

Esto también es importante.

Tu programa **no está modificando archivos protegidos del sistema**.

Está modificando una configuración asociada a **tu sesión de usuario**.

Por eso:

```bash
gsettings set ...
```

normalmente no necesita:

```bash
sudo
```

Tu proceso Python está ejecutándose dentro de tu sesión gráfica:

```text
Usuario Alexi
     │
     ├── GNOME
     ├── gsettings
     └── wallpaper-daemon
```

GNOME permite que las aplicaciones de tu sesión modifiquen determinadas preferencias de tu escritorio.

---

# 6. ¿Qué significa `org.gnome.desktop.background`?

Esta parte:

```text
org.gnome.desktop.background
```

es el **schema** de configuración de GNOME.

Piensa en él como un namespace:

```text
org.gnome.desktop.background
```

y dentro existen diferentes propiedades:

```text
picture-uri
picture-uri-dark
picture-options
primary-color
secondary-color
color-shading-type
...
```

Tu programa está modificando dos:

```python
("picture-uri", "picture-uri-dark")
```

---

# 7. ¿Por qué tienes `picture-uri` y `picture-uri-dark`?

Esto está relacionado con el problema que descubriste anteriormente con el modo oscuro.

Tu código hace:

```python
for key in ("picture-uri", "picture-uri-dark"):
```

y por cada una ejecuta:

```bash
gsettings set ...
```

Así tienes:

```text
picture-uri
      ↓
wallpaper para modo claro

picture-uri-dark
      ↓
wallpaper para modo oscuro
```

Por eso tu parche solucionó el problema de que el wallpaper no cambiara correctamente dependiendo del modo de GNOME.

---

# 8. Después entra `scheduler.py`

Tu programa no cambia el wallpaper constantemente.

Hace esto:

```python
while True:
```

selecciona una imagen:

```python
wallpaper = random.choice(remaining)
```

y llama:

```python
set_wallpaper(wallpaper)
```

Después:

```python
time.sleep(interval)
```

Por ejemplo:

```text
10:00
 ↓
wallpaper A

10:02
 ↓
wallpaper B

10:04
 ↓
wallpaper C

10:06
 ↓
wallpaper D
```

La arquitectura actual es:

```text
main.py
   │
   ├── scanner.py
   │       │
   │       └── encuentra imágenes
   │
   └── scheduler.py
           │
           ├── selecciona imagen
           │
           └── wallpaper.py
                   │
                   └── gsettings
```

---

# 9. `scanner.py` no tiene nada que ver directamente con GNOME

Esto:

```python
for path in directory.rglob("*"):
```

recorre las carpetas.

Después:

```python
if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
```

filtra:

```text
.jpg
.jpeg
.png
.webp
```

Y devuelve:

```python
list[Path]
```

Por ejemplo:

```python
[
    Path("/home/alexi/.local/share/backgrounds/a.jpg"),
    Path("/home/alexi/.local/share/backgrounds/b.png"),
    Path("/home/alexi/.local/share/backgrounds/c.webp"),
]
```

---

# 10. Entonces tu programa realmente es bastante simple

Conceptualmente:

```text
                wallpaper-daemon
                       │
             ┌─────────┴─────────┐
             │                   │
        filesystem            scheduler
             │                   │
       busca imágenes       selecciona imagen
                                 │
                                 ▼
                          wallpaper.py
                                 │
                                 ▼
                           subprocess
                                 │
                                 ▼
                             gsettings
                                 │
                                 ▼
                              GNOME
```

Y esto es precisamente lo interesante del proyecto.

No necesitas una librería Python especializada para controlar el wallpaper.

Estás utilizando una **API/interfaz del sistema operativo** disponible mediante CLI.

---

# 11. ¿Podría Python modificar GNOME directamente?

Sí.

Y aquí aparece una posible evolución interesante.

Actualmente tienes:

```text
Python
  ↓
subprocess
  ↓
gsettings CLI
  ↓
GSettings
```

Podrías eventualmente tener:

```text
Python
  ↓
GSettings / D-Bus
  ↓
GNOME
```

Eso eliminaría la dependencia de ejecutar el proceso externo `gsettings` cada vez.

Pero **no lo haría todavía**.

Para este proyecto tu solución actual tiene una ventaja enorme:

### Es extremadamente simple.

---

# 12. ¿Qué optimizaría del proyecto actual?

Hay varias cosas.

## A. No hacer `gsettings` dos veces

Actualmente:

```python
for key in ("picture-uri", "picture-uri-dark"):
```

genera dos procesos:

```text
Python
 ├── subprocess → gsettings
 │
 └── subprocess → gsettings
```

Podrías abstraer esto mejor, aunque seguirás necesitando modificar ambas claves.

---

## B. `scanner.py` puede ser más eficiente

Actualmente:

```python
directory.rglob("*")
```

recorre todo el árbol.

Si tienes:

```text
backgrounds/
├── anime/
├── games/
├── nature/
├── wallpapers/
├── old/
└── ...
```

lo va a recorrer completo.

Para una colección pequeña está perfectamente bien.

Pero si llegas a tener:

```text
50.000 imágenes
```

podría ser interesante:

* cachear resultados
* detectar modificaciones
* utilizar `os.scandir`
* no volver a escanear todo innecesariamente

---

# 13. El mayor problema arquitectónico actual

Tu `scheduler` es:

```python
while True:
    ...
    time.sleep(interval)
```

Esto funciona.

Pero es un daemon bastante básico.

Una versión más avanzada debería tener algo como:

```text
WallpaperDaemon
│
├── Scanner
├── WallpaperProvider
├── DisplayManager
├── Scheduler
├── Configuration
└── State
```

Y entonces podrías implementar:

```bash
wallpaper-manager start
wallpaper-manager stop
wallpaper-manager next
wallpaper-manager status
wallpaper-manager displays
wallpaper-manager set --monitor HDMI-1 image.jpg
```

Eso convertiría el proyecto en algo mucho más interesante.

---

# 14. Ahora la pregunta importante: ¿dos monitores?

## Sí, absolutamente.

Pero hay una distinción importante.

Actualmente haces:

```bash
gsettings set org.gnome.desktop.background picture-uri ...
```

Eso representa **el wallpaper del escritorio de GNOME**, no:

```text
Monitor 1 → imagen A
Monitor 2 → imagen B
```

Por eso actualmente ambos monitores terminan mostrando el mismo fondo.

---

# 15. Lo que quieres conseguir

Idealmente:

```text
┌──────────────────────┐    ┌──────────────────────┐
│                      │    │                      │
│     wallpaper A      │    │     wallpaper B      │
│                      │    │                      │
│      HDMI-1          │    │      DP-1            │
│                      │    │                      │
└──────────────────────┘    └──────────────────────┘
```

Y el daemon podría tener:

```python
wallpapers = {
    "HDMI-1": Path("mountain.jpg"),
    "DP-1": Path("city.jpg"),
}
```

Entonces:

```text
HDMI-1 → mountain.jpg
DP-1   → city.jpg
```

---

# 16. Pero aquí viene el detalle técnico importante

**GNOME no ofrece mediante `gsettings` una propiedad sencilla del tipo:**

```text
picture-uri-monitor-1
picture-uri-monitor-2
```

Tu implementación actual está utilizando el mecanismo de wallpaper del escritorio GNOME.

Para manejar wallpapers independientes por monitor hay que utilizar otro enfoque.

Una posibilidad es utilizar la información de los monitores mediante:

```bash
xrandr
```

pero **eso depende de X11** y no es la solución adecuada para GNOME moderno sobre Wayland.

Y aquí es donde el proyecto puede ponerse realmente interesante.

---

# 17. GNOME + Wayland cambia las cosas

Tu Ubuntu moderno probablemente está utilizando:

```text
GNOME
   ↓
Wayland
```

en lugar de:

```text
GNOME
   ↓
X11
```

Puedes comprobarlo con:

```bash
echo $XDG_SESSION_TYPE
```

Si aparece:

```text
wayland
```

estás en Wayland.

Y para un proyecto moderno, yo diseñaría el soporte pensando primero en **Wayland/GNOME**, no en X11.

---

# 18. Una arquitectura mucho mejor

Podríamos evolucionar tu proyecto hacia:

```text
                 wallpaper-daemon
                        │
              ┌─────────┴─────────┐
              │                   │
           Scanner            DisplayManager
              │                   │
              │            ┌──────┴──────┐
              │            │             │
              │         Monitor 1     Monitor 2
              │            │             │
              └────────────┴─────────────┘
                           │
                    WallpaperBackend
                           │
                    ┌──────┴───────┐
                    │              │
                  GNOME          Future
                 Backend         Backend
```

Por ejemplo:

```python
class WallpaperBackend:
    def set_wallpaper(self, monitor, image):
        ...
```

Entonces:

```python
backend.set_wallpaper(
    monitor="HDMI-1",
    image=Path("mountain.jpg")
)
```

---

# 19. También podrías detectar automáticamente los monitores

Por ejemplo:

```text
DisplayManager
      │
      ▼
Detect displays
      │
      ├── eDP-1
      └── HDMI-1
```

Y producir:

```python
[
    Display(
        name="eDP-1",
        width=1920,
        height=1080,
        primary=True
    ),

    Display(
        name="HDMI-1",
        width=2560,
        height=1440,
        primary=False
    )
]
```

Después el scheduler podría asignar:

```text
eDP-1
 ↓
wallpaper_01.jpg

HDMI-1
 ↓
wallpaper_02.jpg
```

---

# 20. Incluso puedes hacer modos

Esto sería bastante bueno para tu proyecto.

### Modo `shared`

```text
Monitor 1 ── wallpaper A
Monitor 2 ── wallpaper A
```

### Modo `independent`

```text
Monitor 1 ── wallpaper A
Monitor 2 ── wallpaper B
```

### Modo `synchronized`

```text
Monitor 1 ── wallpaper A
Monitor 2 ── wallpaper B

         ↓ 2 minutos

Monitor 1 ── wallpaper C
Monitor 2 ── wallpaper D
```

### Modo `static`

```text
Monitor 1 ── A
Monitor 2 ── B
```

Nunca cambian.

---

# 21. Y hay otra mejora interesante

Actualmente tienes:

```python
wallpaper = random.choice(remaining)
```

Eso significa que **todos los monitores comparten el mismo ciclo**.

Podríamos pasar a:

```text
Scheduler
   │
   ├── Monitor 1 scheduler
   │       └── A → C → E → G
   │
   └── Monitor 2 scheduler
           └── B → D → F → H
```

Así cada monitor tendría su propio estado.

Por ejemplo:

```python
display_state = {
    "eDP-1": {
        "current": wallpaper_a,
        "remaining": [...]
    },
    "HDMI-1": {
        "current": wallpaper_b,
        "remaining": [...]
    }
}
```

Esto ya empieza a parecer un **wallpaper daemon real**, no simplemente un script que ejecuta `gsettings`.

---

# 22. ¿Qué haría yo con tu proyecto?

No saltaría directamente a D-Bus ni intentaría meter una GUI.

Haría esta evolución:

```text
V1 actual
│
├── Scanner
├── Scheduler
└── GNOME gsettings
        ↓
V2
│
├── Display detection
├── Display model
├── Per-monitor state
└── Independent wallpapers
        ↓
V3
│
├── CLI
├── start
├── stop
├── next
├── status
└── monitor selection
        ↓
V4
│
├── GIF
├── Video
├── Dynamic wallpapers
└── Better media handling
        ↓
V5
│
└── Rust implementation
```

Y **mantendría Python como primera implementación** porque te permite experimentar rápidamente con las APIs de Linux/GNOME.

Después puedes hacer exactamente el mismo proyecto en Rust y comparar:

```text
Python implementation
        VS
Rust implementation
```

que era precisamente una de las partes interesantes de este proyecto.

---

## En resumen

Tu código actualmente hace algo mucho más sencillo de lo que parece:

```text
Path
 ↓
file:// URI
 ↓
subprocess.run()
 ↓
gsettings
 ↓
GSettings
 ↓
GNOME
 ↓
Wallpaper
```

No tiene permisos especiales ni está manipulando directamente el kernel, GPU o framebuffer.

Y **sí, puedes llegar a tener un wallpaper diferente en cada monitor**, pero eso requiere introducir un `DisplayManager` y cambiar el backend actual basado únicamente en `gsettings`, porque la propiedad que estás utilizando representa el fondo del escritorio de GNOME y no un fondo independiente por monitor.

De hecho, **esa sería una muy buena siguiente iteración de tu repositorio**: primero detectar correctamente `eDP-1`, `HDMI-1`, `DP-1`, etc.; después diseñar una abstracción `Display`; y finalmente investigar el mecanismo correcto de GNOME/Wayland para aplicar una imagen individual a cada salida.
