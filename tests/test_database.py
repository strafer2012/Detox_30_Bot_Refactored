import pytest
import aiosqlite

from src.database.database import set_buddy, add_points, get_user_id_by_username

@pytest.mark.asyncio
async def test_set_buddy_creates_pair():
    """Test that set_buddy correctly creates a mutual pair."""
    # Create two test users
    async with aiosqlite.connect("test_detox30.db") as db:
        await db.execute("INSERT INTO users (user_id, username) VALUES (1, 'user1'), (2, 'user2')")
        await db.commit()
    
    result = await set_buddy(1, 2)
    assert result is True
    
    # Check both sides
    async with aiosqlite.connect("test_detox30.db") as db:
        cursor = await db.execute("SELECT buddy_id FROM users WHERE user_id = 1")
        row1 = await cursor.fetchone()
        cursor = await db.execute("SELECT buddy_id FROM users WHERE user_id = 2")
        row2 = await cursor.fetchone()
    
    assert row1[0] == 2
    assert row2[0] == 1

@pytest.mark.asyncio
async def test_add_points():
    """Test that add_points correctly adds points."""
    async with aiosqlite.connect("test_detox30.db") as db:
        await db.execute("INSERT INTO users (user_id, points) VALUES (1, 0)")
        await db.commit()
    
    await add_points(1, 10, "test")
    
    async with aiosqlite.connect("test_detox30.db") as db:
        cursor = await db.execute("SELECT points FROM users WHERE user_id = 1")
        points = (await cursor.fetchone())[0]
    
    assert points == 10

@pytest.mark.asyncio
async def test_get_user_id_by_username_case_insensitive():
    """Test that username search is case-insensitive."""
    async with aiosqlite.connect("test_detox30.db") as db:
        await db.execute("INSERT INTO users (user_id, username) VALUES (1, 'TestUser')")
        await db.commit()
    
    result = await get_user_id_by_username("testuser")
    assert result == 1
    
    result = await get_user_id_by_username("TESTUSER")
    assert result == 1