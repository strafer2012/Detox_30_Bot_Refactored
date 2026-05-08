import pytest
from unittest.mock import AsyncMock, patch

from src.handlers.start import process_buddy_input, BuddyStates

@pytest.mark.asyncio
async def test_process_buddy_input_rejects_self():
    """Test that user cannot select themselves as buddy."""
    # Mock message
    message = AsyncMock()
    message.from_user.id = 123
    message.text = "123"  # same as user_id
    
    state = AsyncMock()
    
    await process_buddy_input(message, state)
    
    # Should send error message
    message.answer.assert_called()
    call_args = message.answer.call_args[0][0]
    assert "нельзя выбрать самого себя" in call_args.lower()

@pytest.mark.asyncio
async def test_process_buddy_input_accepts_valid_id():
    """Test that valid buddy ID is accepted."""
    message = AsyncMock()
    message.from_user.id = 123
    message.text = "456"  # different user
    
    state = AsyncMock()
    
    # Mock the database check (buddy doesn't have a buddy yet)
    with patch('src.handlers.start.aiosqlite.connect') as mock_connect:
        mock_cursor = AsyncMock()
        mock_cursor.fetchone.return_value = (None,)  # no buddy
        mock_connect.return_value.__aenter__.return_value.execute.return_value = mock_cursor
        
        await process_buddy_input(message, state)
    
    # Should send request to buddy
    message.answer.assert_called()
    assert state.clear.called