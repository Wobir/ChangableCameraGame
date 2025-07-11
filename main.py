import pygame as pg

pg.init()

# Константы
WINDOW_SIZE = (800, 600)
HALF_WINDOW = (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)
FPS = 60
GRAVITY = 4
FULLCAM = (0,0, *WINDOW_SIZE)
# Настройка экрана
screen = pg.display.set_mode(WINDOW_SIZE, flags=pg.SCALED, vsync=1)
pg.display.set_caption("ChangableCamera")
CLOCK = pg.time.Clock()
font_system = pg.font.SysFont(None, 24)


class WorldBorder:
    """
    Класс описывает границу мира с начальной и конечной позицией.

    Атрибуты:
        pos (pg.Vector3): начальная точка границы
        pos_end (pg.Vector3): конечная точка границы
    """
    def __init__(self, pos, pos_end):
        self.pos = pg.Vector3(pos)
        self.pos_end = pg.Vector3(pos_end)



class Object:
    """
        Базовый класс для всех объектов в мире.

        Атрибуты:
            pos (pg.Vector3): позиция объекта в 3D пространстве
            visible_pos (pg.Vector3): визуальная позиция (может отличаться в будущем)
            form (str): тип формы ("circle", "rect")
    """
    def __init__(self, pos, form):
        self.pos = pg.Vector3(pos)
        self.visible_pos = pg.Vector3(pos)
        self.form = form

    def draw(self, relative_pos, relative_scale, window):
        """
        Отрисовывает объект на поверхности.

        Args:
            relative_pos (tuple): координаты относительно камеры
            relative_scale (tuple): масштаб по x и y
            window (Surface): окно для отрисовки
        """
        if self.form == "circle":
            pg.draw.circle(window, (40, 40, 255), relative_pos, 20 * relative_scale[0])
        elif self.form == "rect":
            pg.draw.rect(window, (255, 40, 40), (*relative_pos, 100 * relative_scale[0], 30 * relative_scale[1]))


# Класс поведения для игрока
class Player(Object):
    """
    Игрок — управляемый объект с гравитацией.

    Атрибуты:
        v_speed (float): вертикальная скорость
        grounded (bool): находится ли игрок на земле
        radius (int): радиус игрока (для коллизий)
    """

    def __init__(self, pos, form):
        super().__init__(pos, form)
        self.v_speed = 0
        self.grounded = False
        self.radius = 20  # TODO: Сделать параметр, лучше от картинки

    def controller(self, keys):
        """
        Обработка клавиш управления.

        Args:
            keys (dict): словарь нажатых клавиш
        """
        if keys[100]:
            self.pos.x += 10
        if keys[97]:
            self.pos.x -= 10
        if keys[119]:
            self.pos.z -= 10
        if keys[115]:
            self.pos.z += 10
        if keys[32] and self.grounded:
            self.grounded = False
            self.v_speed = -50

    def update(self):
        """Обновляет физику игрока (гравитация и столкновение с полом)."""
        if not self.grounded:
            self.pos.y += self.v_speed
            self.v_speed += GRAVITY
            if self.radius + self.pos.y >= WINDOW_SIZE[1]:
                self.grounded = True
                self.pos.y = WINDOW_SIZE[1] - self.radius
                self.v_speed = 0



class Camera:
    """
    Камера для отображения разных проекций мира.

    Атрибуты:
        active (bool): активность камеры
        plane (str): плоскость отображения ('XY', 'XZ', 'ZY')
        rect (tuple): прямоугольник области камеры
        scaleX (float): масштабирование по X
        scaleY (float): масштабирование по Y
        txt (Surface): текстовое представление плоскости
    """
    def __init__(self, plane, dimensions):
        if plane=="XZ":
            self.active = True
        else:
            self.active = False
        self.plane = plane
        self.x = dimensions[0]
        self.y = dimensions[1]
        self.width = dimensions[2]
        self.height = dimensions[3]
        self.rect = (self.x, self.y, self.width, self.height)
        self.scaleX = self.width / WINDOW_SIZE[0]
        self.scaleY = self.height / WINDOW_SIZE[1]
        self.txt = font_system.render(self.plane, True, (255, 255, 255))

    def set_size(self, dimensions):
        self.x = dimensions[0]
        self.y = dimensions[1]
        self.width = dimensions[2]
        self.height = dimensions[3]
        self.rect = (self.x, self.y, self.width, self.height)
        self.scaleX = self.width / WINDOW_SIZE[0]
        self.scaleY = self.height / WINDOW_SIZE[1]
    def draw(self, window, objs_draw=None):
        """
        Отрисовывает камеру и объекты внутри неё.

        Args:
            window (Surface): окно Pygame
            objs_draw (list): список объектов для отрисовки
        """
        pg.draw.rect(window, (50, 50, 50), self.rect)
        pg.draw.rect(window, (100, 100, 100), self.rect, 2)
        if objs_draw:
            for obj_draw in objs_draw:
                if self.plane == "XY":
                    obj_draw.draw((obj_draw.pos.x * self.scaleX + self.x, obj_draw.pos.y * self.scaleY + self.y),
                                  (self.scaleX, self.scaleY), window)
                if self.plane == "XZ":
                    obj_draw.draw((obj_draw.pos.x * self.scaleX + self.x, obj_draw.pos.z * self.scaleY + self.y),
                                  (self.scaleX, self.scaleY), window)
                if self.plane == "ZY":
                    obj_draw.draw((obj_draw.pos.z * self.scaleX + self.x, obj_draw.pos.y * self.scaleY + self.y),
                                  (self.scaleX, self.scaleY), window)
        window.blit(self.txt, (self.x + 20, self.y + 20))

# Создание первичных объектов
circle = Player((0, 0, 0), "circle")
objects = [circle]

# Создание камер
cameras_dimensions= [(0, 0, *HALF_WINDOW),
(HALF_WINDOW[0], 0, *HALF_WINDOW),
(0, HALF_WINDOW[1], *HALF_WINDOW),
(*HALF_WINDOW, *HALF_WINDOW)]
camera1 = Camera("XZ", cameras_dimensions[0])
camera2 = Camera("ZY", cameras_dimensions[1])
camera3 = Camera("XY", cameras_dimensions[2])
camera4 = Camera("Inventory", cameras_dimensions[3])
cameras = [camera1, camera2, camera3, camera4]
for i in cameras:
    i.set_size(FULLCAM)
# Основной цикл
running = True
time_last = 0

def draw_game():
    screen.fill((255, 255, 255))
    for cam in cameras:
        if cam.active:
            cam.draw(screen, objects)

def update_game():
    circle.controller(pg.key.get_pressed())
    circle.update()

while running:
    dt = CLOCK.tick(FPS)
    time_last += dt
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key in [pg.K_1, pg.K_2, pg.K_3, pg.K_4]:
                for i in cameras:
                    i.active = False
                    i.set_size(FULLCAM)
                if event.key == pg.K_1:
                    camera1.active = True
                elif event.key == pg.K_2:
                    camera2.active = True
                elif event.key == pg.K_3:
                    camera3.active = True
                elif event.key == pg.K_4:
                    camera4.active = True
            if event.key == pg.K_5:
                for i in range(len(cameras)):
                    cameras[i].set_size(cameras_dimensions[i])
                    cameras[i].active = True

    if time_last >= 15:
        update_game()
        time_last = 0

    draw_game()

    pg.display.flip()

pg.quit()