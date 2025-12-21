from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select
from app.database.models import Base, User, Dialog, Message, Manager
from config.settings import DATABASE_URL
from datetime import datetime

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with async_session_maker() as session:
        yield session

async def get_or_create_user(session: AsyncSession, telegram_id: str, username: str = None, first_name: str = None, last_name: str = None):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    return user

async def get_or_create_dialog(session: AsyncSession, user_id: int, bot_name: str):
    result = await session.execute(
        select(Dialog).where(Dialog.user_id == user_id, Dialog.bot_name == bot_name)
    )
    dialog = result.scalar_one_or_none()
    
    if not dialog:
        dialog = Dialog(user_id=user_id, bot_name=bot_name)
        session.add(dialog)
        await session.commit()
        await session.refresh(dialog)
    
    return dialog

async def create_message(session: AsyncSession, dialog_id: int, text: str, is_from_user: bool = True, telegram_message_id: int = None):
    message = Message(
        dialog_id=dialog_id,
        text=text,
        is_from_user=1 if is_from_user else 0,
        telegram_message_id=telegram_message_id
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message

async def update_dialog_status(session: AsyncSession, dialog_id: int, status: str):
    result = await session.execute(select(Dialog).where(Dialog.id == dialog_id))
    dialog = result.scalar_one_or_none()
    
    if dialog:
        dialog.status = status
        dialog.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(dialog)
    
    return dialog

async def get_dialog_by_id(session: AsyncSession, dialog_id: int):
    result = await session.execute(
        select(Dialog)
        .options(selectinload(Dialog.user))
        .where(Dialog.id == dialog_id)
    )
    return result.scalar_one_or_none()

async def get_all_dialogs(session: AsyncSession):
    result = await session.execute(
        select(Dialog)
        .options(selectinload(Dialog.user))
        .order_by(Dialog.updated_at.desc())
    )
    return result.scalars().all()

async def get_dialog_messages(session: AsyncSession, dialog_id: int):
    result = await session.execute(
        select(Message)
        .where(Message.dialog_id == dialog_id)
        .order_by(Message.created_at)
    )
    return result.scalars().all()

async def get_manager_by_username(session: AsyncSession, username: str):
    result = await session.execute(select(Manager).where(Manager.username == username))
    return result.scalar_one_or_none()