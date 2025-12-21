import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from flask import Flask
from threading import Thread
import os

from config.settings import BOT_TOKENS, SECRET_KEY
from app.database.crud import init_db
from app.bot.middlewares.bot_identifier import BotIdentifierMiddleware
from app.web.routes.auth import auth_bp
from app.web.routes.dialogs import dialogs_bp

logging.basicConfig(level=logging.INFO)

manager_bot = None

async def start_bot(bot_name: str, token: str):
    global manager_bot
    
    from app.bot.handlers import user_handlers, manager_handlers
    
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    dp.message.middleware(BotIdentifierMiddleware(bot_name))
    
    from aiogram import Router, F
    from aiogram.types import Message
    from aiogram.filters import Command
    from app.services.message_service import MessageService
    from app.services.notification_service import NotificationService
    from config.settings import MANAGER_GROUP_ID
    from app.database.crud import async_session_maker
    from sqlalchemy import select
    from app.database.models import User, Dialog
    
    user_router = Router()
    manager_router = Router()
    
    @user_router.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer(
            "Здравствуйте! Напишите ваше сообщение, и менеджер свяжется с вами."
        )
    
    @user_router.message(F.text)
    async def handle_user_message(message: Message, bot_name: str):
        dialog, user, msg = await MessageService.process_user_message(
            telegram_id=str(message.from_user.id),
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            text=message.text,
            bot_name=bot_name,
            telegram_message_id=message.message_id
        )
        
        if manager_bot:
            await NotificationService.send_new_message_notification(manager_bot, dialog, user, msg)
        
        await message.answer("Ваше сообщение получено. Ожидайте ответа менеджера.")
    
    @manager_router.message(F.chat.id == MANAGER_GROUP_ID, F.reply_to_message)
    async def handle_manager_reply(message: Message):
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
    
    dp.include_router(user_router)
    dp.include_router(manager_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    logging.info(f"Бот {bot_name} запущено")
    await dp.start_polling(bot)

async def start_all_bots():
    global manager_bot
    
    await init_db()
    
    if not BOT_TOKENS.get("bot1"):
        logging.error("BOT_TOKEN_1 не налаштовано! Це бот для групи менеджерів.")
        return
    
    manager_bot = Bot(token=BOT_TOKENS["bot1"], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await manager_bot.delete_webhook(drop_pending_updates=True)
    logging.info(f"✓ Manager Bot ініціалізовано")
    
    dp_manager = Dispatcher()
    
    from aiogram import Router, F
    from aiogram.types import Message
    from config.settings import MANAGER_GROUP_ID
    from app.services.message_service import MessageService
    from app.database.crud import async_session_maker
    from sqlalchemy import select
    from app.database.models import User, Dialog
    
    manager_router = Router()
    
    @manager_router.message(F.chat.id == MANAGER_GROUP_ID, F.reply_to_message)
    async def handle_manager_reply(message: Message):
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
    
    dp_manager.include_router(manager_router)
    
    tasks = [dp_manager.start_polling(manager_bot)]
    
    for bot_name, token in BOT_TOKENS.items():
        if bot_name != "bot1" and token:
            tasks.append(start_bot(bot_name, token))
    
    if len(tasks) == 1:
        logging.error("Немає налаштованих user ботів! Додайте BOT_TOKEN_2, BOT_TOKEN_3, BOT_TOKEN_4")
        return
    
    logging.info(f"✓ Запускається {len(tasks)} ботів...")
    await asyncio.gather(*tasks)

def run_flask_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'web', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'web', 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.secret_key = SECRET_KEY
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dialogs_bp)
    
    print(f"✓ Template folder: {template_dir}")
    print(f"✓ Static folder: {static_dir}")
    print(f"✓ Web interface: http://127.0.0.1:5000")
    print(f"✓ Login: admin | Password: password123")
    
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    
    try:
        asyncio.run(start_all_bots())
    except KeyboardInterrupt:
        print("\n✓ Систему зупинено")