from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.database.crud import (
    async_session_maker, get_all_dialogs, get_dialog_by_id, 
    get_dialog_messages, create_message, update_dialog_status
)
from app.services.message_service import MessageService
from aiogram import Bot
from config.settings import BOT_TOKENS
import asyncio
from functools import wraps

dialogs_bp = Blueprint("dialogs", __name__)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "manager" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper

@dialogs_bp.route("/")
@login_required
def dashboard():
    async def get_dialogs():
        async with async_session_maker() as db_session:
            return await get_all_dialogs(db_session)
    
    dialogs = asyncio.run(get_dialogs())
    return render_template("dashboard.html", dialogs=dialogs)

@dialogs_bp.route("/dialog/<int:dialog_id>")
@login_required
def dialog_view(dialog_id):
    async def get_data():
        async with async_session_maker() as db_session:
            dialog = await get_dialog_by_id(db_session, dialog_id)
            messages = await get_dialog_messages(db_session, dialog_id)
            return dialog, messages
    
    dialog, messages = asyncio.run(get_data())
    return render_template("dialog.html", dialog=dialog, messages=messages)

@dialogs_bp.route("/dialog/<int:dialog_id>/reply", methods=["POST"])
@login_required
def send_reply(dialog_id):
    text = request.json.get("text")
    
    async def process_reply():
        async with async_session_maker() as db_session:
            dialog = await get_dialog_by_id(db_session, dialog_id)
            
            await MessageService.process_manager_reply(dialog_id, text)
            
            bot = Bot(token=BOT_TOKENS.get(dialog.bot_name))
            
            try:
                await bot.send_message(
                    chat_id=int(dialog.user.telegram_id),
                    text=f"Ответ менеджера:\n\n{text}"
                )
            finally:
                await bot.session.close()
    
    asyncio.run(process_reply())
    return jsonify({"status": "success"})

@dialogs_bp.route("/dialog/<int:dialog_id>/status", methods=["POST"])
@login_required
def change_status(dialog_id):
    status = request.json.get("status")
    
    async def update_status():
        async with async_session_maker() as db_session:
            await update_dialog_status(db_session, dialog_id, status)
    
    asyncio.run(update_status())
    return jsonify({"status": "success"})