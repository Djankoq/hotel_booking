import asyncio
import random
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.models import User, Hotel, Room, Booking
from app.models.booking import BookingStatus

NUM_RANDOM_USERS = 8
NUM_HOTELS = 20
MIN_ROOMS_PER_HOTEL = 5
MAX_ROOMS_PER_HOTEL = 15
NUM_RANDOM_BOOKINGS = 50

fake = Faker("ru_RU")

async def seed_data():
    """
    Основная функция для генерации и вставки данных в БД.
    """
    engine = create_async_engine(str(settings.DATABASE_URL))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    print("Подключение к базе данных...")
    async with session_factory() as session:
        print("Очистка старых данных...")
        await session.execute(delete(Booking))
        await session.execute(delete(Room))
        await session.execute(delete(Hotel))
        await session.execute(delete(User))
        await session.commit()
        print("Старые данные удалены.")

        print("Создание пользователей...")
        users = []
        
        manager_user = User(
            first_name="Admin", last_name="Manager", login="manager@test.com",
            password_hash=hash_password("password123"), is_manager=True
        )
        regular_user = User(
            first_name="John", last_name="Doe", login="user@test.com",
            password_hash=hash_password("password123"), is_manager=False
        )
        users.extend([manager_user, regular_user])

        for _ in range(NUM_RANDOM_USERS):
            users.append(User(
                first_name=fake.first_name(), last_name=fake.last_name(),
                login=fake.unique.email(), password_hash=hash_password("password123"), is_manager=False
            ))
            
        session.add_all(users)
        await session.commit()
        print(f"Создано {len(users)} пользователей.")

        await session.refresh(manager_user)
        await session.refresh(regular_user)

        print(f"Создание {NUM_HOTELS} отелей...")
        hotels = []
        for _ in range(NUM_HOTELS):
            hotels.append(Hotel(
                name=f"Отель «{fake.word().capitalize()}»", location=fake.city(),
                description=fake.text(max_nb_chars=200), manager_id=manager_user.id,
                image_url=f"https://picsum.photos/seed/{random.randint(1, 1000)}/800/600"
            ))
        session.add_all(hotels)
        await session.commit()
        print("Отели созданы.")

        print("Создание комнат...")
        all_rooms = []
        for hotel in hotels:
            for _ in range(random.randint(MIN_ROOMS_PER_HOTEL, MAX_ROOMS_PER_HOTEL)):
                all_rooms.append(Room(
                    hotel_id=hotel.id, name=f"{random.choice(['Стандарт', 'Люкс', 'Делюкс', 'Семейный'])}",
                    price_per_night=Decimal(random.randrange(2500, 15000)), capacity=random.randint(1, 4),
                    description=fake.sentence(), image_url=f"https://picsum.photos/seed/{random.randint(1, 1000)}/400/300"
                ))
        session.add_all(all_rooms)
        await session.commit()
        print("Комнаты созданы.")

        print("Создание бронирований...")
        bookings = []

        bookings.append(Booking(
            room_id=all_rooms[0].id, user_id=regular_user.id,
            check_in=date.today() - timedelta(days=10), check_out=date.today() - timedelta(days=5),
            total_price=all_rooms[0].price_per_night * 5, status=BookingStatus.confirmed
        ))
        bookings.append(Booking(
            room_id=all_rooms[1].id, user_id=regular_user.id,
            check_in=date.today() + timedelta(days=2), check_out=date.today() + timedelta(days=4),
            total_price=all_rooms[1].price_per_night * 2, status=BookingStatus.pending
        ))
        bookings.append(Booking(
            room_id=all_rooms[2].id, user_id=manager_user.id,
            check_in=date.today() + timedelta(days=20), check_out=date.today() + timedelta(days=25),
            total_price=all_rooms[2].price_per_night * 5, status=BookingStatus.pending
        ))

        for _ in range(NUM_RANDOM_BOOKINGS):
            room = random.choice(all_rooms)
            user = random.choice(users)
            check_in_date = date.today() + timedelta(days=random.randint(-60, 60))
            check_out_date = check_in_date + timedelta(days=random.randint(2, 14))
            bookings.append(Booking(
                room_id=room.id, user_id=user.id, check_in=check_in_date, check_out=check_out_date,
                total_price=room.price_per_night * (check_out_date - check_in_date).days,
                status=random.choice(list(BookingStatus))
            ))
            
        session.add_all(bookings)
        await session.commit()
        print(f"Создано {len(bookings)} бронирований.")

    await engine.dispose()
    print("Генерация данных завершена!")

if __name__ == "__main__":
    asyncio.run(seed_data())
