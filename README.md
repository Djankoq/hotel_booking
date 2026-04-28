как завпустить

1. Установить Git и Docker Desktop
2. Настройка переменных окружения
Для Linux/macOS:
cp .env.example .env

Для Windows (PowerShell):
copy .env.example .env

3. Убедиться что в .env заполнен SECRET_KEY и указан правильный DATABASE_URL для Docker
4. Сборка и запуск контейнеров

docker compose up --build -d

5. Применение миграций (Создание таблиц)
docker compose exec app alembic upgrade head

6. Если все шаги выполнены успешно, API доступно по адресам:

Swagger: http://localhost:8000/docs

Остановка проекта: docker compose down


Скрипт генарции данных: docker exec -it hotel_app_container python -m scripts.seed
Скрипт очистки данных:  docker exec -it hotel_app_container python -m scripts.clear_data          
