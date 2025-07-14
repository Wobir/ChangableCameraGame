import pygame as pg

pg.init()

# Константы
WINDOW_SIZE = (800, 600)
HALF_WINDOW = (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)
FPS = 60
GRAVITY = 4
FULLCAM = (0, 0, *WINDOW_SIZE)

# Экран и системные компоненты
screen = pg.display.set_mode(WINDOW_SIZE, flags=pg.SCALED, vsync=1)
pg.display.set_caption("ChangableCamera")
CLOCK = pg.time.Clock()
font_system = pg.font.SysFont(None, 24)


class WorldBorder:
    """Определяет границы игрового мира."""

    def __init__(self, pos: tuple, pos_end: tuple):
        """
        Args:
            pos (tuple): Начальная позиция границы мира.
            pos_end (tuple): Конечная позиция границы мира.
        """
        self.pos = pg.Vector3(pos)
        self.pos_end = pg.Vector3(pos_end)


class Object:
    """Базовый класс объекта в 3D-пространстве."""

    def __init__(self, pos: tuple, form: str):
        """
        Args:
            pos (tuple): Позиция объекта в 3D.
            form (str): Форма объекта: 'circle' или 'rect'.
        """
        self.pos = pg.Vector3(pos)
        self.visible_pos = pg.Vector3(pos)
        self.form = form

    def draw(self, relative_pos: tuple, relative_scale: tuple, window: pg.Surface) -> None:
        """
        Отрисовка объекта на экране.

        Args:
            relative_pos (tuple): Позиция относительно камеры.
            relative_scale (tuple): Масштаб по осям X и Y.
            window (Surface): Поверхность отрисовки.
        """
        if self.form == "circle":
            pg.draw.circle(window, (40, 40, 255), relative_pos, 20 * relative_scale[0])
        elif self.form == "rect":
            pg.draw.rect(window, (255, 40, 40),
                         (*relative_pos, 100 * relative_scale[0], 30 * relative_scale[1]))


class Player(Object):
    """Класс игрока — управляемый объект с гравитацией."""

    def __init__(self, pos: tuple, form: str):
        super().__init__(pos, form)
        self.v_speed = 0
        self.grounded = False
        self.radius = 20

    def controller(self, keys: pg.key.ScancodeWrapper) -> None:
        """Обработка ввода с клавиатуры.

        Args:
            keys: Состояние клавиш.
        """
        speed = 10
        if keys[pg.K_d]:
            self.pos.x += speed
        if keys[pg.K_a]:
            self.pos.x -= speed
        if keys[pg.K_w]:
            self.pos.z -= speed
        if keys[pg.K_s]:
            self.pos.z += speed
        if keys[pg.K_SPACE] and self.grounded:
            self.grounded = False
            self.v_speed = -50

        # Ограничение в пределах мира
        self.pos.x = max(world_border.pos.x, min(self.pos.x, world_border.pos_end.x))
        self.pos.z = max(world_border.pos.z, min(self.pos.z, world_border.pos_end.z))

    def update(self) -> None:
        """Обновление состояния (гравитация и столкновение с землёй)."""
        if not self.grounded:
            self.pos.y += self.v_speed
            self.v_speed += GRAVITY
            if self.pos.y + self.radius >= WINDOW_SIZE[1]:
                self.grounded = True
                self.pos.y = WINDOW_SIZE[1] - self.radius
                self.v_speed = 0


class Camera:
    """Камера для отображения выбранной проекции мира."""

    def __init__(self, plane: str, dimensions: tuple):
        """
        Args:
            plane (str): Плоскость отображения ('XY', 'XZ', 'ZY').
            dimensions (tuple): Размер и положение камеры.
        """
        self.active = (plane == "XZ")
        self.plane = plane
        self.set_size(dimensions)

    def set_size(self, dimensions: tuple) -> None:
        """Изменить размеры камеры."""
        self.x, self.y, self.width, self.height = dimensions
        self.rect = (self.x, self.y, self.width, self.height)
        self.scaleX = self.width / WINDOW_SIZE[0]
        self.scaleY = self.height / WINDOW_SIZE[1]

    def get_offset(self, target_pos: pg.Vector3) -> pg.Vector2:
        """Считает смещение камеры, чтобы следить за целью."""
        if self.plane == "XY":
            cx = target_pos.x - WINDOW_SIZE[0] / 2
            cy = target_pos.y - WINDOW_SIZE[1] / 2
        elif self.plane == "XZ":
            cx = target_pos.x - WINDOW_SIZE[0] / 2
            cy = target_pos.z - WINDOW_SIZE[1] / 2
        elif self.plane == "ZY":
            cx = target_pos.z - WINDOW_SIZE[0] / 2
            cy = target_pos.y - WINDOW_SIZE[1] / 2
        else:
            return pg.Vector2(0, 0)

        # Ограничение смещения
        max_offset_x = world_border.pos_end.x - WINDOW_SIZE[0]
        max_offset_y = world_border.pos_end.z - WINDOW_SIZE[1]
        cx = max(world_border.pos.x, min(cx, max_offset_x))
        cy = max(world_border.pos.z if self.plane == "XZ" else world_border.pos.y, min(cy, max_offset_y))
        return pg.Vector2(cx, cy)

    def draw(self, window: pg.Surface, objs_draw: list = None) -> None:
        pg.draw.rect(window, (50, 50, 50), self.rect)
        pg.draw.rect(window, (100, 100, 100), self.rect, 2)

        if not objs_draw:
            return

        self.offset = self.get_offset(circle.pos)

        for obj in objs_draw:
            # Проецируем 3D → 2D
            if self.plane == "XY":
                ox, oy = obj.pos.x - self.offset.x, obj.pos.y - self.offset.y
            elif self.plane == "XZ":
                ox, oy = obj.pos.x - self.offset.x, obj.pos.z - self.offset.y
            elif self.plane == "ZY":
                ox, oy = obj.pos.z - self.offset.x, obj.pos.y - self.offset.y
            else:
                continue

            # Не рисуем за пределами
            if 0 <= ox <= WINDOW_SIZE[0] and 0 <= oy <= WINDOW_SIZE[1]:
                draw_pos = (ox * self.scaleX + self.x, oy * self.scaleY + self.y)
                obj.draw(draw_pos, (self.scaleX, self.scaleY), window)

        # Отрисовать текст (название и координаты игрока)
        # Координаты по активной плоскости
        if self.plane == "XZ":
            coord_text = f"X={int(circle.pos.x)} Z={int(circle.pos.z)}"
        elif self.plane == "XY":
            coord_text = f"X={int(circle.pos.x)} Y={int(circle.pos.y)}"
        elif self.plane == "ZY":
            coord_text = f"Z={int(circle.pos.z)} Y={int(circle.pos.y)}"
        else:
            coord_text = "Inventory"
        coord_surface = font_system.render(coord_text, True, (255, 255, 255))
        window.blit(coord_surface, (self.x + 20, self.y + 30))


def draw_game() -> None:
    """Очистка экрана и отрисовка активных камер."""
    screen.fill((255, 255, 255))
    for cam in cameras:
        if cam.active:
            cam.draw(screen, objects)


def update_game() -> None:
    """Обновление состояния мира (физика и ввод)."""
    circle.controller(pg.key.get_pressed())
    circle.update()


# Инициализация мира и объектов
world_border = WorldBorder((-500, 0, -500), (1500, 0, 1500))
platform = Object((300, 580, 300), "rect")
circle = Player((0, 0, 0), "circle")
objects = [platform, circle]

# Инициализация камер
camera_layouts = [
    (0, 0, *HALF_WINDOW),
    (HALF_WINDOW[0], 0, *HALF_WINDOW),
    (0, HALF_WINDOW[1], *HALF_WINDOW),
    (*HALF_WINDOW, *HALF_WINDOW)
]
cameras = [
    Camera("XZ", camera_layouts[0]),
    Camera("ZY", camera_layouts[1]),
    Camera("XY", camera_layouts[2]),
    Camera("Inventory", camera_layouts[3])
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
                    cam.set_size(camera_layouts[i])
                    cam.active = True

    if time_last >= 15:
        update_game()
        time_last = 0

    draw_game()
    pg.display.flip()

pg.quit()
