# Игра «Шарики» — графическое окно через X11
# Запуск: docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix balls-game

FROM python:3.11-slim-bookworm

# Библиотеки для pygame (SDL2) и вывода в X11
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libx11-6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY logic.py game_gui.py gui.py ./

# Точка входа — запуск игры в графическом окне (нужен X11 на хосте)
CMD ["python", "gui.py"]
