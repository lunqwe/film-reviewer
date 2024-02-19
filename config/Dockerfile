FROM python:3.10.0

# Устанавливаем переменные окружения для отображения сообщений в стандартный вывод
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY="django-insecure--*zt#nu$sc@zm+x1jo3ezk*tf3iwt0*uv)ti%=p1020-f7x!j7"
ENV DATABASE_URL="postgres://jobpilot_db_user:7mUSIHqwOwZXHx04phULSr4gzvTIp9XB@dpg-cmm532ol5elc73c9tjb0-a.oregon-postgres.render.com/jobpilot_db"
ENV SENDGRID_API_KEY="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"
ENV DEBUG=True
ENV EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
ENV EMAIL_HOST=smtp.sendgrid.net
ENV EMAIL_PORT=587

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


