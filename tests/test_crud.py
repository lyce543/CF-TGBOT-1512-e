import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, User, Dialog, Message, Manager
from app.database.crud import (
    get_or_create_user,
    get_or_create_dialog,
    create_message,
    update_dialog_status,
    get_dialog_by_id,
    get_all_dialogs,
    get_dialog_messages,
    get_manager_by_username
)

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_get_or_create_user_new(db_session):
    user = await get_or_create_user(
        db_session,
        telegram_id="123456",
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    assert user.telegram_id == "123456"
    assert user.username == "testuser"

@pytest.mark.asyncio
async def test_get_or_create_user_existing(db_session):
    user1 = await get_or_create_user(db_session, telegram_id="123456", username="test1")
    user2 = await get_or_create_user(db_session, telegram_id="123456", username="test2")
    assert user1.id == user2.id

@pytest.mark.asyncio
async def test_get_or_create_dialog_new(db_session):
    user = await get_or_create_user(db_session, telegram_id="123456")
    dialog = await get_or_create_dialog(db_session, user.id, "bot1")
    assert dialog.user_id == user.id
    assert dialog.bot_name == "bot1"

@pytest.mark.asyncio
async def test_get_or_create_dialog_existing(db_session):
    user = await get_or_create_user(db_session, telegram_id="123456")
    dialog1 = await get_or_create_dialog(db_session, user.id, "bot1")
    dialog2 = await get_or_create_dialog(db_session, user.id, "bot1")
    assert dialog1.id == dialog2.id

@pytest.mark.asyncio
async def test_create_message(db_session):
    user = await get_or_create_user(db_session, telegram_id="123456")
    dialog = await get_or_create_dialog(db_session, user.id, "bot1")
    message = await create_message(db_session, dialog.id, "Test message", True, 12345)
    assert message.text == "Test message"
    assert message.is_from_user == 1

@pytest.mark.asyncio
async def test_update_dialog_status(db_session):
    user = await get_or_create_user(db_session, telegram_id="123456")
    dialog = await get_or_create_dialog(db_session, user.id, "bot1")
    updated = await update_dialog_status(db_session, dialog.id, "закрыто")
    assert updated.status == "закрыто"

@pytest.mark.asyncio
async def test_get_dialog_by_id(db_session):
    user = await get_or_create_user(db_session, telegram_id="123456")
    dialog = await get_or_create_dialog(db_session, user.id, "bot1")
    retrieved = await get_dialog_by_id(db_session, dialog.id)
    assert retrieved.id == dialog.id
    assert retrieved.user.telegram_id == "123456"

@pytest.mark.asyncio
async def test_get_dialog_messages(db_session):
    user = await get_or_create_user(db_session, telegram_id="123456")
    dialog = await get_or_create_dialog(db_session, user.id, "bot1")
    await create_message(db_session, dialog.id, "Message 1", True)
    await create_message(db_session, dialog.id, "Message 2", False)
    messages = await get_dialog_messages(db_session, dialog.id)
    assert len(messages) == 2