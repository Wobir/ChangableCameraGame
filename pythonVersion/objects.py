# objects.py
"""
Модуль объектов мира (платформы, базовые формы).
"""
import pygame as pg
from settings import COLORS


class WorldBorder:
    """
    Определяет границы мира.
    """
    def __init__(self, pos: tuple, pos_end: tuple):
        self.pos = pg.Vector3(pos)
        self.pos_end = pg.Vector3(pos_end)


class Object:
    """
    Базовый объект в 3D-пространстве.
    """
    def __init__(self, pos: tuple, form: str):
        """
        Args:
            pos (tuple): Позиция в 3D-пространстве.
            form (str): Форма ('circle' или 'rect').
        """
        self.pos = pg.Vector3(pos)
        self.form = form

    def draw(self, relative_pos: tuple, relative_scale: tuple, surface: pg.Surface , plane: str) -> None:
        """
        Отрисовать объект.

        Args:
            relative_pos (tuple): Позиция относительно камеры.
            relative_scale (tuple): Масштаб по осям.
            surface (Surface): Поверхность отрисовки.
        """
        if self.form == "circle":
            pg.draw.circle(
                surface, COLORS["circle"],
                (int(relative_pos[0]), int(relative_pos[1])),
                int(20 * relative_scale[0])
            )
        elif self.form == "rect":
            pg.draw.rect(
                surface, COLORS["rect"],
                (*relative_pos, 100 * relative_scale[0], 30 * relative_scale[1])
            )


class Cube(Object):
    def __init__(self, pos: tuple, form: str, size_dimensions: tuple):
        super().__init__(pos, form)
        self.size = pg.Vector3(size_dimensions)

    def draw(self, relative_pos: tuple, relative_scale: tuple, surface: pg.Surface, plane: str) -> None:
        if plane == "XZ":
            visual_width = self.size.x
            visual_height = self.size.z
        elif plane == "ZY":
            visual_width = self.size.z
            visual_height = self.size.y
        elif plane == "XY":
            visual_width = self.size.x
            visual_height = self.size.y
        else:
            visual_width, visual_height = 0, 0
        pg.draw.rect(
            surface, COLORS["rect"],
            (*relative_pos, visual_width * relative_scale[0], visual_height * relative_scale[1])
        )