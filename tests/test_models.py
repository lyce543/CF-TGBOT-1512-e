import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, User, Dialog, Message, Manager

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        yield session
    
    await engine.dispose()

def test_user_creation():
    user = User(
        telegram_id="123456789",
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    assert user.telegram_id == "123456789"
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.last_name == "User"

def test_dialog_creation():
    dialog = Dialog(
        user_id=1,
        bot_name="bot1",
        status="новое"
    )
    assert dialog.user_id == 1
    assert dialog.bot_name == "bot1"
    assert dialog.status == "новое"

@pytest.mark.asyncio
async def test_dialog_default_status(db_session):
    dialog = Dialog(user_id=1, bot_name="bot1")
    db_session.add(dialog)
    await db_session.commit()
    await db_session.refresh(dialog)
    assert dialog.status == "новое"

def test_message_creation():
    message = Message(
        dialog_id=1,
        text="Test message",
        is_from_user=1,
        telegram_message_id=12345
    )
    assert message.dialog_id == 1
    assert message.text == "Test message"
    assert message.is_from_user == 1
    assert message.telegram_message_id == 12345

@pytest.mark.asyncio
async def test_message_default_is_from_user(db_session):
    message = Message(dialog_id=1, text="Test")
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    assert message.is_from_user == 1

def test_manager_creation():
    manager = Manager(
        username="admin",
        password_hash="hashed_password"
    )
    assert manager.username == "admin"
    assert manager.password_hash == "hashed_password"