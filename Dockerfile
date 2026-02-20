FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости и ставим их
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry 

RUN poetry config virtualenvs.create false 

RUN poetry install --no-interaction --no-ansi --no-root --only main && \
    pip uninstall -y poetry

# Копируем код приложения
COPY . .

# Создаем папки
RUN mkdir -p /app/logs /app/media /app/static /app/staticfiles && \
    chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "config.wsgi:application"]