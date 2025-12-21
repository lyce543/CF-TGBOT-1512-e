import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.notification_service import NotificationService
from app.database.models import User, Dialog, Message

@pytest.mark.asyncio
async def test_send_new_message_notification_with_username():
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock(return_value=MagicMock())
    
    mock_user = User(
        id=1,
        telegram_id="123456",
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    mock_dialog = Dialog(id=1, user_id=1, bot_name="bot1", status="новое")
    mock_message = Message(id=1, dialog_id=1, text="Test message", is_from_user=1)
    
    with patch('app.services.notification_service.MANAGER_GROUP_ID', -100123456789):
        with patch('app.services.notification_service.WEB_URL', 'http://localhost:5000'):
            result = await NotificationService.send_new_message_notification(
                mock_bot, mock_dialog, mock_user, mock_message
            )
            
            mock_bot.send_message.assert_called_once()
            call_args = mock_bot.send_message.call_args
            assert call_args[1]['chat_id'] == -100123456789
            assert '@testuser' in call_args[1]['text']
            assert 'Test message' in call_args[1]['text']

@pytest.mark.asyncio
async def test_send_new_message_notification_without_username():
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock(return_value=MagicMock())
    
    mock_user = User(
        id=1,
        telegram_id="123456",
        username=None,
        first_name="Test",
        last_name="User"
    )
    mock_dialog = Dialog(id=1, user_id=1, bot_name="bot1", status="новое")
    mock_message = Message(id=1, dialog_id=1, text="Test message", is_from_user=1)
    
    with patch('app.services.notification_service.MANAGER_GROUP_ID', -100123456789):
        with patch('app.services.notification_service.WEB_URL', 'http://localhost:5000'):
            result = await NotificationService.send_new_message_notification(
                mock_bot, mock_dialog, mock_user, mock_message
            )
            
            mock_bot.send_message.assert_called_once()
            call_args = mock_bot.send_message.call_args
            assert 'без username' in call_args[1]['text']

@pytest.mark.asyncio
async def test_send_new_message_notification_error_handling():
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock(side_effect=Exception("Network error"))
    
    mock_user = User(id=1, telegram_id="123456", username="test")
    mock_dialog = Dialog(id=1, user_id=1, bot_name="bot1", status="новое")
    mock_message = Message(id=1, dialog_id=1, text="Test", is_from_user=1)
    
    with patch('app.services.notification_service.MANAGER_GROUP_ID', -100123456789):
        with patch('app.services.notification_service.WEB_URL', 'http://localhost:5000'):
            result = await NotificationService.send_new_message_notification(
                mock_bot, mock_dialog, mock_user, mock_message
            )
            
            assert result is None