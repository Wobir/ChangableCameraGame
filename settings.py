# settings.py
"""
Настройки игры и конфигурация, включая загрузку из JSON.
"""
import json
import os

# Пути к конфигурациям
CONFIG_PATH = "config.json"

# Настройки по умолчанию
WINDOW_SIZE = (800, 600)
HALF_WINDOW = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
FPS = 60
GRAVITY = 4



COLORS = {
    "bg": (255, 255, 255),
    "cam_bg": (50, 50, 50),
    "cam_border": (100, 100, 100),
    "text": (255, 255, 255),
    "circle": (40, 40, 255),
    "rect": (255, 40, 40)
}

# Камеры по умолчанию
DEFAULT_CAMERAS = [
    {"plane": "XZ", "layout_index": 0},
    {"plane": "ZY", "layout_index": 1},
    {"plane": "XY", "layout_index": 2},
    {"plane": "Inventory", "layout_index": 3}
]

# Камера макет (глобально задаётся для всех видов)
CAMERA_LAYOUTS = [
    (0, 0, WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2),
    (WINDOW_SIZE[0] // 2, 0, WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2),
    (0, WINDOW_SIZE[1] // 2, WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2),
    (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2, WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
]

FULLCAM = (0, 0, *WINDOW_SIZE)


def load_config():
    """
    Загрузка настроек игры из JSON-конфига, если доступен.
    """
    global GRAVITY, FPS
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            GRAVITY = config.get("gravity", GRAVITY)
            FPS = config.get("fps", FPS)
            return config
    return {}
