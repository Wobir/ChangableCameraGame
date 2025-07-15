# main.py
"""
Главный модуль запуска игры с камерами, игроком и интерфейсом.
Настройки читаются из config.json. Компоненты структурированы по модулям.
"""
import pygame as pg
from camera import Camera
from player import Player
from objects import Object, WorldBorder, Cube
from settings import (
    WINDOW_SIZE, FPS, FULLCAM,
    COLORS, CAMERA_LAYOUTS, load_config
)

pg.init()

# Системные компоненты
screen = pg.display.set_mode(WINDOW_SIZE, flags=pg.SCALED, vsync=1)
pg.display.set_caption("ChangableCamera")
CLOCK = pg.time.Clock()
font_system = pg.font.SysFont(None, 24)

# Загрузка настроек
config = load_config()

# Инициализация мира и объектов
world_border = WorldBorder(config["world_border"]["pos"], config["world_border"]["pos_end"])
platform = Cube((300, 480, 300), "rect", (200,100,150))
circle = Player(tuple(config["player"]["start_pos"]), config["player"]["form"])
objects = [ platform, circle]

# Инициализация камер
cameras = [
    Camera("XZ", CAMERA_LAYOUTS[0], world_border, font_system, circle),
    Camera("ZY", CAMERA_LAYOUTS[1], world_border, font_system, circle),
    Camera("XY", CAMERA_LAYOUTS[2], world_border, font_system, circle),
    Camera("Inventory", CAMERA_LAYOUTS[3], world_border, font_system, circle)
]
for cam in cameras:
    cam.set_size(FULLCAM)

# Игровой цикл
running = True
time_last = 0

while running:
    dt = CLOCK.tick(FPS)
    time_last += dt

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key in [pg.K_1, pg.K_2, pg.K_3, pg.K_4]:
                for cam in cameras:
                    cam.active = False
                    cam.set_size(FULLCAM)
                cameras[event.key - pg.K_1].active = True
            elif event.key == pg.K_5:
                for i, cam in enumerate(cameras):
                    cam.set_size(CAMERA_LAYOUTS[i])
                    cam.active = True

    if time_last >= 15:
        circle.controller(pg.key.get_pressed(), world_border)
        circle.update()
        time_last = 0

    screen.fill(COLORS["bg"])
    for cam in cameras:
        if cam.active:
            cam.draw(screen, objects)

    # FPS-счётчик
    fps = int(CLOCK.get_fps())
    fps_surface = font_system.render(f"FPS: {fps}", True, COLORS["text"])
    screen.blit(fps_surface, (10, 10))

    pg.display.flip()

pg.quit()
