from aiogram import Router, F, Bot
from aiogram.types import Message
from config.settings import MANAGER_GROUP_ID
from app.database.crud import async_session_maker
from app.services.message_service import MessageService
from sqlalchemy import select
from app.database.models import User, Dialog

router = Router()

@router.message(F.chat.id == MANAGER_GROUP_ID, F.reply_to_message)
async def handle_manager_reply(message: Message, bot: Bot):
    reply_text = message.reply_to_message.text
    
    if "Бот:" not in reply_text:
        return
    
    lines = reply_text.split("\n")
    bot_name = None
    username = None
    
    for line in lines:
        if line.startswith("Бот:"):
            bot_name = line.replace("Бот:", "").strip()
        if "(@" in line:
            username_start = line.find("@")
            username_end = line.find(")", username_start)
            if username_start != -1 and username_end != -1:
                username = line[username_start+1:username_end]
    
    if not bot_name or not username or username == "без username":
        await message.reply("❌ Не вдалося визначити користувача")
        return
    
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if user:
            result = await session.execute(
                select(Dialog).where(Dialog.user_id == user.id, Dialog.bot_name == bot_name)
            )
            dialog = result.scalar_one_or_none()
            
            if dialog:
                await MessageService.process_manager_reply(dialog.id, message.text)
                
                from config.settings import BOT_TOKENS
                reply_bot = Bot(token=BOT_TOKENS.get(bot_name))
                
                try:
                    await reply_bot.send_message(
                        chat_id=int(user.telegram_id),
                        text=f"Ответ менеджера:\n\n{message.text}"
                    )
                    await message.reply("✅ Ответ отправлен пользователю")
                except Exception as e:
                    await message.reply(f"❌ Ошибка отправки: {e}")
                finally:
                    await reply_bot.session.close()
            else:
                await message.reply("❌ Діалог не знайдено")
        else:
            await message.reply("❌ Користувач не знайдено")
