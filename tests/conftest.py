import pytest
import asyncio
import aiosqlite
import os

TEST_DB = "test_detox30.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def setup_test_db():
    # Create fresh test database before each test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    async with aiosqlite.connect(TEST_DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                buddy_id INTEGER,
                current_day INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                timezone INTEGER DEFAULT 7,
                is_active BOOLEAN DEFAULT 1,
                registration_date DATE DEFAULT CURRENT_DATE
            )
        """)
        await db.commit()
    
    # Temporarily override DATABASE_PATH
    import src.database.database as db_module
    db_module.DATABASE_PATH = TEST_DB
    
    yield
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)