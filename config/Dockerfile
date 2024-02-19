FROM python:3.10.0

# Устанавливаем переменные окружения для отображения сообщений в стандартный вывод
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию в контейнере
WORKDIR /config

# Устанавливаем зависимости проекта
COPY requirements.txt /config/
RUN pip install --no-cache-dir -r requirements.txt
# Устанавливаем bash в качестве оболочки по умолчанию
SHELL ["/bin/bash", "-c"]

# Копируем файлы проекта в контейнер
COPY . /config/

# Открываем порт 8000 для веб-сервера Django
EXPOSE 8000

# Запускаем сервер Django
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]


