import asyncio

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Убедитесь, что пути импорта корректны
from app.core.config import settings
from app.models import Booking, Room, Hotel, User


async def clear_all_data():
    """
    Основная функция для полной очистки данных в таблицах.
    """
    engine = create_async_engine(str(settings.DATABASE_URL))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    print("Подключение к базе данных...")
    async with session_factory() as session:
        print("Начинаю очистку таблиц...")
        # Удаляем в обратном порядке из-за внешних ключей
        # Booking -> Room -> Hotel -> User
        await session.execute(delete(Booking))
        await session.execute(delete(Room))
        await session.execute(delete(Hotel))
        await session.execute(delete(User))
        await session.commit()
        print("Все таблицы успешно очищены.")

    await engine.dispose()
    print("Операция завершена!")

if __name__ == "__main__":
    print("ВНИМАНИЕ: Этот скрипт полностью удалит все данные из таблиц Users, Hotels, Rooms и Bookings.")
    confirm = input("Вы уверены, что хотите продолжить? (y/n): ")
    if confirm.lower() == 'y':
        asyncio.run(clear_all_data())
    else:
        print("Операция отменена.")
