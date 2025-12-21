import asyncio
from app.database.crud import init_db, async_session_maker
from app.database.models import Manager
from werkzeug.security import generate_password_hash

async def setup_database():
    print("Створення таблиць в базі даних...")
    await init_db()
    print("✓ Таблиці створено")
    
    print("Створення адміністратора...")
    async with async_session_maker() as session:
        manager = Manager(
            username='admin',
            password_hash=generate_password_hash('password123')
        )
        session.add(manager)
        await session.commit()
    print("✓ Адміністратор створений (логін: admin, пароль: password123)")
    print("\nБаза даних готова до використання!")

if __name__ == "__main__":
    asyncio.run(setup_database())