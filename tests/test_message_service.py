import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.message_service import MessageService
from app.database.models import User, Dialog, Message

@pytest.mark.asyncio
async def test_process_user_message_new_dialog():
    with patch('app.services.message_service.async_session_maker') as mock_session_maker:
        mock_session = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        
        mock_user = User(id=1, telegram_id="123456", username="test")
        mock_dialog = Dialog(id=1, user_id=1, bot_name="bot1", status="новое")
        mock_message = Message(id=1, dialog_id=1, text="Test", is_from_user=1)
        
        with patch('app.services.message_service.get_or_create_user', return_value=mock_user):
            with patch('app.services.message_service.get_or_create_dialog', return_value=mock_dialog):
                with patch('app.services.message_service.create_message', return_value=mock_message):
                    with patch('app.services.message_service.update_dialog_status') as mock_update:
                        dialog, user, message = await MessageService.process_user_message(
                            telegram_id="123456",
                            username="test",
                            first_name="Test",
                            last_name="User",
                            text="Test message",
                            bot_name="bot1",
                            telegram_message_id=12345
                        )
                        
                        assert dialog.id == 1
                        assert user.id == 1
                        assert message.text == "Test"
                        mock_update.assert_called_once()

@pytest.mark.asyncio
async def test_process_user_message_closed_dialog():
    with patch('app.services.message_service.async_session_maker') as mock_session_maker:
        mock_session = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        
        mock_user = User(id=1, telegram_id="123456", username="test")
        mock_dialog = Dialog(id=1, user_id=1, bot_name="bot1", status="закрыто")
        mock_message = Message(id=1, dialog_id=1, text="Test", is_from_user=1)
        
        with patch('app.services.message_service.get_or_create_user', return_value=mock_user):
            with patch('app.services.message_service.get_or_create_dialog', return_value=mock_dialog):
                with patch('app.services.message_service.create_message', return_value=mock_message):
                    with patch('app.services.message_service.update_dialog_status') as mock_update:
                        await MessageService.process_user_message(
                            telegram_id="123456",
                            username="test",
                            first_name="Test",
                            last_name="User",
                            text="Test message",
                            bot_name="bot1",
                            telegram_message_id=12345
                        )
                        
                        mock_update.assert_called()

@pytest.mark.asyncio
async def test_process_manager_reply():
    with patch('app.services.message_service.async_session_maker') as mock_session_maker:
        mock_session = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        
        mock_message = Message(id=1, dialog_id=1, text="Reply", is_from_user=0)
        
        with patch('app.services.message_service.create_message', return_value=mock_message):
            with patch('app.services.message_service.update_dialog_status') as mock_update:
                message = await MessageService.process_manager_reply(1, "Reply text")
                
                assert message.text == "Reply"
                assert message.is_from_user == 0
                mock_update.assert_called_once_with(mock_session, 1, "закрыто")