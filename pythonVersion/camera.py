# camera.py
"""
Модуль камеры — отображение сцены в выбранной плоскости.
"""
import pygame as pg
from settings import WINDOW_SIZE, COLORS


class Camera:
    """
    Камера для проекции мира в 2D в зависимости от плоскости.
    """

    def __init__(self, plane: str, dimensions: tuple, world_border, font, target):
        """
        Args:
            plane (str): Ось проекции ('XY', 'XZ', 'ZY').
            dimensions (tuple): Область отрисовки.
            world_border (WorldBorder): Ограничение мира.
            font (Font): Шрифт для текста.
            target (Object): Объект, за которым следит камера.
        """
        self.plane = plane
        self.active = (plane == "XZ")
        self.world_border = world_border
        self.font = font
        self.target = target
        self.set_size(dimensions)

    def set_size(self, dimensions: tuple) -> None:
        """Задать размеры камеры."""
        self.x, self.y, self.width, self.height = dimensions
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.scaleX = self.width / WINDOW_SIZE[0]
        self.scaleY = self.height / WINDOW_SIZE[1]

    def get_offset(self, target_pos: pg.Vector3) -> pg.Vector2:
        """Рассчитать смещение камеры для слежения."""
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

        max_x = self.world_border.pos_end.x - WINDOW_SIZE[0]
        max_y = self.world_border.pos_end.z - WINDOW_SIZE[1]

        cx = max(self.world_border.pos.x, min(cx, max_x))
        cy = max(
            self.world_border.pos.z if self.plane == "XZ" else self.world_border.pos.y,
            min(cy, max_y)
        )
        return pg.Vector2(cx, cy)

    def draw(self, window: pg.Surface, objs_draw: list = None) -> None:
        """
        Отрисовка сцены.

        Args:
            window (Surface): Поверхность.
            objs_draw (list): Объекты для отрисовки.
        """
        pg.draw.rect(window, COLORS["cam_bg"], self.rect)
        pg.draw.rect(window, COLORS["cam_border"], self.rect, 2)

        if not objs_draw:
            return

        self.offset = self.get_offset(self.target.pos)

        for obj in objs_draw:
            if self.plane == "XY":
                ox, oy = obj.pos.x - self.offset.x, obj.pos.y - self.offset.y
            elif self.plane == "XZ":
                ox, oy = obj.pos.x - self.offset.x, obj.pos.z - self.offset.y
            elif self.plane == "ZY":
                ox, oy = obj.pos.z - self.offset.x, obj.pos.y - self.offset.y
            else:
                continue

            if 0 <= ox <= WINDOW_SIZE[0] and 0 <= oy <= WINDOW_SIZE[1]:
                draw_pos = (ox * self.scaleX + self.x, oy * self.scaleY + self.y)
                obj.draw(draw_pos, (self.scaleX, self.scaleY), window, self.plane)

        # Отрисовка координат
        if self.plane == "XZ":
            coords = f"X={int(self.target.pos.x)} Z={int(self.target.pos.z)}"
        elif self.plane == "XY":
            coords = f"X={int(self.target.pos.x)} Y={int(self.target.pos.y)}"
        elif self.plane == "ZY":
            coords = f"Z={int(self.target.pos.z)} Y={int(self.target.pos.y)}"
        else:
            coords = "Inventory"

        coord_surface = self.font.render(coords, True, COLORS["text"])
        window.blit(coord_surface, (self.x + 20, self.y + 30))
