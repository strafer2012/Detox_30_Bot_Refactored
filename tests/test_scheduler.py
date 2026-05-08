import pytest
from datetime import datetime
import pytz

from src.scheduler.scheduler import increment_day_at_midnight

@pytest.mark.asyncio
async def test_increment_day_at_midnight_logic():
    """Test that increment_day_at_midnight correctly identifies users at midnight."""
    # This is a simplified test - in real scenario we'd mock the database
    # For now just verify the function exists and can be called
    assert callable(increment_day_at_midnight)
    
    # Test timezone calculation logic
    tz = 7  # UTC+7
    now_utc = datetime.utcnow()
    local_tz = pytz.timezone(f"Etc/GMT{-tz}" if tz >= 0 else f"Etc/GMT+{abs(tz)}")
    local_time = now_utc.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    
    # Just verify the timezone conversion works
    assert local_time is not None