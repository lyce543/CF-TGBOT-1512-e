from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import MANAGER_GROUP_ID, WEB_URL

class NotificationService:
    @staticmethod
    async def send_new_message_notification(bot: Bot, dialog, user, message):
        username_text = f"@{user.username}" if user.username else "без username"
        user_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "Без імені"
        
        text = (
            f"📩 Новое сообщение\n\n"
            f"Бот: {dialog.bot_name}\n"
            f"От: {user_name} ({username_text})\n"
            f"Текст: {message.text}\n\n"
            f"Статус: {dialog.status}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Открыть диалог", 
                url=f"{WEB_URL}/dialog/{dialog.id}"
            )]
        ])
        
        try:
            sent_message = await bot.send_message(
                chat_id=MANAGER_GROUP_ID,
                text=text,
                reply_markup=keyboard
            )
            return sent_message
        except Exception as e:
            print(f"Помилка відправки уведомлення: {e}")
            return None