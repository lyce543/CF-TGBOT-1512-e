from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class BotIdentifierMiddleware(BaseMiddleware):
    def __init__(self, bot_name: str):
        self.bot_name = bot_name
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["bot_name"] = self.bot_name
        return await handler(event, data)
