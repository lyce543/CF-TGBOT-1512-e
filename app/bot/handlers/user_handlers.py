from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from app.services.message_service import MessageService
from app.services.notification_service import NotificationService

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Здравствуйте! Напишите ваше сообщение, и менеджер свяжется с вами."
    )

@router.message(F.text)
async def handle_user_message(message: Message, bot_name: str, bot: Bot):
    dialog, user, msg = await MessageService.process_user_message(
        telegram_id=str(message.from_user.id),
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        text=message.text,
        bot_name=bot_name,
        telegram_message_id=message.message_id
    )
    
    await NotificationService.send_new_message_notification(bot, dialog, user, msg)
    
    await message.answer("Ваше сообщение получено. Ожидайте ответа менеджера.")
