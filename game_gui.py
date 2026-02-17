"""
Графический интерфейс для игры про шарики.
Использует logic.py для движения, смешивания цветов и всасывания/выпускания.
"""

import random
import sys

import pygame

from logic import GameLogic, Ball

# --- Настройки (можно менять в начале кода) ---
START_BALL_COUNT = 12
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (255, 255, 255)

# Цвета для стартовых шариков (разнообразная палитра)
START_COLORS = [
    (255, 0, 0), (0, 150, 255), (0, 200, 80), (255, 180, 0),
    (180, 0, 255), (255, 100, 150), (0, 200, 200), (200, 100, 0),
]


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Шарики — всасывание и смешивание")
    clock = pygame.time.Clock()

    logic = GameLogic(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

    # Стартовые шарики со случайными позициями и цветами
    for _ in range(START_BALL_COUNT):
        x = random.uniform(80, SCREEN_WIDTH - 80)
        y = random.uniform(80, SCREEN_HEIGHT - 80)
        vx = random.uniform(-2, 2)
        vy = random.uniform(-2, 2)
        r, g, b = random.choice(START_COLORS)
        logic.add_ball(x, y, vx, vy, r, g, b)

    # Шрифт для подсказок и счётчика инвентаря
    font = pygame.font.Font(None, 28)
    font_big = pygame.font.Font(None, 36)

    running = True
    last_time = pygame.time.get_ticks() / 1000.0

    while running:
        current_time = pygame.time.get_ticks() / 1000.0
        dt = min(current_time - last_time, 0.1)
        last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                logic.screen_width = event.w
                logic.screen_height = event.h
                logic.set_delete_zone(
                    event.w - 80, event.h - 60, 80, 60
                )
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    # ЛКМ: если под курсором шарик — всасываем; иначе — выпускаем в точку клика
                    sucked = logic.suck_at(mx, my)
                    if sucked is None and logic.inventory:
                        logic.spit_at(mx, my)
                elif event.button == 3 and logic.inventory:
                    logic.spit_at(mx, my)

        logic.update(dt)

        # Рисуем
        screen.fill(BACKGROUND_COLOR)

        # Зона удаления (правый нижний угол)
        dx, dy, dw, dh = logic.get_delete_zone()
        delete_rect = pygame.Rect(int(dx), int(dy), int(dw), int(dh))
        pygame.draw.rect(screen, (255, 200, 200), delete_rect)
        pygame.draw.rect(screen, (220, 80, 80), delete_rect, 3)
        label = font_big.render("УДАЛИТЬ", True, (180, 50, 50))
        screen.blit(label, (dx + (dw - label.get_width()) // 2, dy + (dh - label.get_height()) // 2))

        # Шарики
        for ball in logic.balls:
            pos = (int(ball.x), int(ball.y))
            r = int(ball.radius)
            color = (ball.r, ball.g, ball.b)
            pygame.draw.circle(screen, color, pos, r)
            # Обводка для читаемости
            pygame.draw.circle(screen, (80, 80, 80), pos, r, 1)

        # Подсказка и инвентарь (маленькие кружки — цвет удерживаемых шариков)
        inv_text = font.render(f"В инвентаре: {len(logic.inventory)}", True, (60, 60, 60))
        screen.blit(inv_text, (12, 12))
        for i, ball in enumerate(logic.inventory[-5:]):  # не более 5 кружков
            px, py = 14 + i * 22, 38
            pygame.draw.circle(screen, ball.color, (px, py), 8)
            pygame.draw.circle(screen, (60, 60, 60), (px, py), 8, 1)
        hint = font.render("ЛКМ: всасывать / выпускать шарик | ПКМ: выпустить в курсор", True, (100, 100, 100))
        screen.blit(hint, (12, screen.get_height() - 28))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
