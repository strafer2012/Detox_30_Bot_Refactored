import aiosqlite
from config.settings import DATABASE_PATH


async def init_db():
    """Initialize database tables."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS buddy_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER,
                user2_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    print('✅ Database initialized')


async def migrate_database():
    """Run database migrations."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Add any missing columns if needed
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in await cursor.fetchall()]
        
        if 'is_paid' not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN is_paid BOOLEAN DEFAULT 0")
        if 'current_message_id' not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN current_message_id INTEGER")
        
        await db.commit()
    print('✅ Database migrated')


async def set_buddy(user_id: int, buddy_id: int) -> bool:
    """Set buddy relationship."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET buddy_id = ? WHERE user_id = ?", (buddy_id, user_id))
        await db.execute("UPDATE users SET buddy_id = ? WHERE user_id = ?", (user_id, buddy_id))
        await db.commit()
    return True


async def get_user_id_by_username(username: str):
    """Get user ID by username (case-insensitive)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)", 
            (username,)
        )
        row = await cursor.fetchone()
    return row[0] if row else None


async def add_points(user_id: int, amount: int, reason: str = ""):
    """Add points to user."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET points = points + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()
    return True

print('✅ database.py loaded with all functions')