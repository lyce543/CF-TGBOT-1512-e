from app.database.crud import (
    get_or_create_user, get_or_create_dialog, create_message, 
    update_dialog_status, async_session_maker
)

class MessageService:
    @staticmethod
    async def process_user_message(telegram_id: str, username: str, first_name: str, 
                                   last_name: str, text: str, bot_name: str, 
                                   telegram_message_id: int):
        async with async_session_maker() as session:
            user = await get_or_create_user(session, telegram_id, username, first_name, last_name)
            dialog = await get_or_create_dialog(session, user.id, bot_name)
            
            if dialog.status == "закрыто":
                await update_dialog_status(session, dialog.id, "новое")
            
            message = await create_message(session, dialog.id, text, True, telegram_message_id)
            
            return dialog, user, message
    
    @staticmethod
    async def process_manager_reply(dialog_id: int, text: str):
        async with async_session_maker() as session:
            message = await create_message(session, dialog_id, text, False)
            await update_dialog_status(session, dialog_id, "закрыто")
            return message