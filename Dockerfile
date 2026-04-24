# Используем официальный легковесный образ Python
FROM python:3.11-slim

# Задаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости для работы с PostgreSQL
# gcc и libpq-dev часто нужны для сборки драйверов БД под Linux
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Сначала копируем только файл зависимостей (для кэширования слоев Docker)
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь оставшийся код проекта внутрь контейнера
COPY . .

# Команда, которая выполнится при старте контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]