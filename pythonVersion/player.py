# player.py
"""
Модуль игрока и логики гравитации/прыжка.
"""
import pygame as pg
from settings import GRAVITY, WINDOW_SIZE, COLORS, KEYS
from objects import Object


class Player(Object):
    """
    Игрок с управлением, гравитацией и прыжком.
    """
    def __init__(self, pos: tuple, form: str):
        super().__init__(pos, form)
        self.v_speed = 0
        self.grounded = False
        self.radius = 20
        self.jump_anim = 0

    def controller(self, keys: pg.key.ScancodeWrapper, world_border) -> None:
        """
        Управление игроком (WASD + прыжок).

        Args:
            keys: Нажатые клавиши.
            world_border: Ограничения по карте.
        """
        speed = 10
        if keys[KEYS['D_SC']]:
            self.pos.x += speed
        if keys[KEYS['A_SC']]:
            self.pos.x -= speed
        if keys[KEYS['W_SC']]:
            self.pos.z -= speed
        if keys[KEYS['S_SC']]:
            self.pos.z += speed

        if keys[KEYS['SPACE_SC']] and self.grounded:
            self.grounded = False
            self.v_speed = -50
            self.jump_anim = 10

        # Границы мира
        self.pos.x = max(world_border.pos.x, min(self.pos.x, world_border.pos_end.x))
        self.pos.z = max(world_border.pos.z, min(self.pos.z, world_border.pos_end.z))

    def update(self) -> None:
        """
        Применение гравитации и логика приземления.
        """
        if not self.grounded:
            self.pos.y += self.v_speed
            self.v_speed += GRAVITY
            if self.pos.y + self.radius >= WINDOW_SIZE[1]:
                self.grounded = True
                self.pos.y = WINDOW_SIZE[1] - self.radius
                self.v_speed = 0



    def draw(self, relative_pos: tuple, relative_scale: tuple, surface: pg.Surface, plane: str) -> None:
        """
        Отрисовка игрока с анимацией прыжка.

        Args:
            relative_pos: Положение на экране.
            relative_scale: Масштаб.
            surface: Поверхность отрисовки.
        """
        
        pg.draw.circle(
            surface, COLORS["circle"],
            (int(relative_pos[0]), int(relative_pos[1])),
            int(self.radius * relative_scale[0])
        )
