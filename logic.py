"""
Модуль игровой логики для игры про шарики.
Только логика, без визуального интерфейса.
"""

import math
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Set


@dataclass
class Ball:
    """Шарик с позицией, скоростью и цветом."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 15.0
    r: int = 255
    g: int = 0
    b: int = 0
    _id: int = field(default=0, repr=False)

    @property
    def pos(self) -> Tuple[float, float]:
        return (self.x, self.y)

    @property
    def color(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def set_color(self, r: int, g: int, b: int) -> None:
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))


class GameLogic:
    """
    Игровая логика: движение, инвентарь, смешивание цветов, зона удаления.
    """

    def __init__(
        self,
        screen_width: float = 800,
        screen_height: float = 600,
        delete_zone: Optional[Tuple[float, float, float, float]] = None
    ):
        """
        Args:
            screen_width, screen_height: размеры экрана
            delete_zone: (x, y, width, height) — зона удаления шариков.
                         По умолчанию — правый нижний угол 80x60.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.balls: List[Ball] = []
        self.inventory: List[Ball] = []
        self._next_id = 1

        if delete_zone is None:
            dz_w, dz_h = 80, 60
            self.delete_zone = (
                screen_width - dz_w,
                screen_height - dz_h,
                dz_w, dz_h
            )
        else:
            self.delete_zone = delete_zone

        # Радиус «всасывания» мышкой
        self.suck_radius = 50.0
        # Скорость выплёвывания
        self.spit_speed = 8.0

    def _create_ball(
        self,
        x: float, y: float,
        vx: float = 0.0, vy: float = 0.0,
        r: int = 255, g: int = 0, b: int = 0
    ) -> Ball:
        ball = Ball(x=x, y=y, vx=vx, vy=vy, r=r, g=g, b=b)
        ball._id = self._next_id
        self._next_id += 1
        return ball

    def add_ball(
        self,
        x: float, y: float,
        vx: float = 0.0, vy: float = 0.0,
        r: int = 255, g: int = 0, b: int = 0
    ) -> Ball:
        """Добавить шарик на экран."""
        ball = self._create_ball(x, y, vx, vy, r, g, b)
        self.balls.append(ball)
        return ball

    # --- Движение ---

    def update(self, dt: float) -> None:
        """
        Обновить состояние игры на dt секунд.
        Движение шариков, отскок от стен, смешивание при касании,
        проверка зоны удаления.
        """
        self._move_balls(dt)
        self._bounce_walls()
        self._mix_colors_on_contact()
        self._remove_in_delete_zone()

    def _move_balls(self, dt: float) -> None:
        for b in self.balls:
            b.x += b.vx * dt
            b.y += b.vy * dt

    def _bounce_walls(self) -> None:
        for b in self.balls:
            if b.x - b.radius < 0:
                b.x = b.radius
                b.vx = abs(b.vx)
            if b.x + b.radius > self.screen_width:
                b.x = self.screen_width - b.radius
                b.vx = -abs(b.vx)
            if b.y - b.radius < 0:
                b.y = b.radius
                b.vy = abs(b.vy)
            if b.y + b.radius > self.screen_height:
                b.y = self.screen_height - b.radius
                b.vy = -abs(b.vy)

    def _mix_colors_on_contact(self) -> None:
        """
        При касании шарики смешивают цвета.
        Используем смешение, дающее насыщенные цвета — избегаем белого.
        """
        n = len(self.balls)
        touched_pairs: Set[Tuple[int, int]] = set()

        for i in range(n):
            for j in range(i + 1, n):
                bi, bj = self.balls[i], self.balls[j]
                dist = math.hypot(bi.x - bj.x, bi.y - bj.y)
                if dist <= bi.radius + bj.radius and (i, j) not in touched_pairs:
                    touched_pairs.add((i, j))
                    r, g, b = self._mix_colors(
                        (bi.r, bi.g, bi.b),
                        (bj.r, bj.g, bj.b)
                    )
                    bi.set_color(r, g, b)
                    bj.set_color(r, g, b)

    def _mix_colors(
        self,
        c1: Tuple[int, int, int],
        c2: Tuple[int, int, int]
    ) -> Tuple[int, int, int]:
        """
        Смешивание цветов с акцентом на насыщенные оттенки.
        Избегаем блеклого белого: используем смесь среднего и «субтрактивного».
        """
        r1, g1, b1 = c1
        r2, g2, b2 = c2

        # Среднее RGB
        ar = (r1 + r2) // 2
        ag = (g1 + g2) // 2
        ab = (b1 + b2) // 2

        # Субтрактивное смешение (как краски) — даёт более тёмные, интересные цвета
        sr = max(0, (r1 * r2) // 255)
        sg = max(0, (g1 * g2) // 255)
        sb = max(0, (b1 * b2) // 255)

        # Комбинация: 60% субтрактивное + 40% среднее — богатый, не белый результат
        r = int(0.6 * sr + 0.4 * ar)
        g = int(0.6 * sg + 0.4 * ag)
        b = int(0.6 * sb + 0.4 * ab)

        # Не допускаем слишком светлый (беловатый) цвет
        total = r + g + b
        if total > 550:
            scale = 550 / total
            r = int(r * scale)
            g = int(g * scale)
            b = int(b * scale)

        return (
            max(0, min(255, r)),
            max(0, min(255, g)),
            max(0, min(255, b))
        )

    def _remove_in_delete_zone(self) -> None:
        """Удалить шарики, попавшие в зону удаления."""
        dx, dy, dw, dh = self.delete_zone
        to_remove = []
        for b in self.balls:
            if dx <= b.x <= dx + dw and dy <= b.y <= dy + dh:
                to_remove.append(b)
        for b in to_remove:
            self.balls.remove(b)

    # --- Инвентарь: всасывание и выплёвывание ---

    def suck_at(self, mouse_x: float, mouse_y: float) -> Optional[Ball]:
        """
        «Всасывание» шарика мышкой. Возвращает втянутый шарик или None.
        """
        best = None
        best_dist = self.suck_radius

        for b in self.balls:
            d = math.hypot(b.x - mouse_x, b.y - mouse_y)
            if d <= self.suck_radius and d < best_dist:
                best_dist = d
                best = b

        if best is not None:
            self.balls.remove(best)
            self.inventory.append(best)
            return best
        return None

    def spit_at(
        self,
        mouse_x: float,
        mouse_y: float,
        direction_angle: Optional[float] = None
    ) -> Optional[Ball]:
        """
        «Выплюнуть» шарик в указанную точку.
        direction_angle: угол направления в радианах (0 = вправо).
        Если None — направление от центра экрана к точке клика.
        """
        if not self.inventory:
            return None
        ball = self.inventory.pop()
        ball.x = mouse_x
        ball.y = mouse_y

        if direction_angle is not None:
            angle = direction_angle
        else:
            cx = self.screen_width / 2
            cy = self.screen_height / 2
            angle = math.atan2(mouse_y - cy, mouse_x - cx)

        ball.vx = math.cos(angle) * self.spit_speed
        ball.vy = math.sin(angle) * self.spit_speed
        self.balls.append(ball)
        return ball

    # --- Утилиты ---

    def get_delete_zone(self) -> Tuple[float, float, float, float]:
        """(x, y, width, height) — зона удаления."""
        return self.delete_zone

    def set_delete_zone(self, x: float, y: float, w: float, h: float) -> None:
        self.delete_zone = (x, y, w, h)
