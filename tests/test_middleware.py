import pytest
from unittest.mock import AsyncMock, MagicMock
from app.bot.middlewares.bot_identifier import BotIdentifierMiddleware

@pytest.mark.asyncio
async def test_bot_identifier_middleware():
    middleware = BotIdentifierMiddleware("bot1")
    
    handler = AsyncMock(return_value="result")
    event = MagicMock()
    data = {}
    
    result = await middleware(handler, event, data)
    
    assert data["bot_name"] == "bot1"
    assert result == "result"
    handler.assert_called_once_with(event, data)

@pytest.mark.asyncio
async def test_bot_identifier_middleware_preserves_existing_data():
    middleware = BotIdentifierMiddleware("bot2")
    
    handler = AsyncMock(return_value="result")
    event = MagicMock()
    data = {"existing_key": "existing_value"}
    
    await middleware(handler, event, data)
    
    assert data["bot_name"] == "bot2"
    assert data["existing_key"] == "existing_value"

@pytest.mark.asyncio
async def test_bot_identifier_middleware_different_bots():
    middleware1 = BotIdentifierMiddleware("bot1")
    middleware2 = BotIdentifierMiddleware("bot2")
    
    handler = AsyncMock()
    event = MagicMock()
    data1 = {}
    data2 = {}
    
    await middleware1(handler, event, data1)
    await middleware2(handler, event, data2)
    
    assert data1["bot_name"] == "bot1"
    assert data2["bot_name"] == "bot2"