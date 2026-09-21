# wallpaper-daemon

Perfecto. Entonces **por ahora trabajamos únicamente en Python**. La versión Rust queda para después.

Para esta primera versión, mantendría el proyecto simple pero bien estructurado:

```text
wallpaper-manager/
├── src/
│   ├── main.py
│   ├── scanner.py
│   ├── wallpaper.py
│   ├── scheduler.py
│   └── config.py
├── tests/
├── pyproject.toml
└── README.md
```

### V1

Implementaremos, en este orden:

1. **Scanner** → encontrar wallpapers en las carpetas configuradas.
2. **Wallpaper controller** → cambiar el fondo de GNOME.
3. **Selector** → elegir aleatoriamente sin repetir.
4. **Scheduler** → cambiar cada X minutos.
5. **Config** → carpetas, intervalo y modo de selección.
6. **CLI** → comandos como `next`, `start`, `stop` y `status`.
7. **Tests** → probar cada componente.

No metería todavía GUI, IA, clasificación de imágenes ni D-Bus.

**Primer objetivo:** conseguir que Python pueda detectar tus imágenes y cambiar correctamente el wallpaper de GNOME. Después construimos encima de eso.

