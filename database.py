import aiosqlite
from src.config.settings import DATABASE_PATH
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                buddy_id INTEGER,
                current_day INTEGER DEFAULT 1,
                points INTEGER DEFAULT 0,
                timezone INTEGER DEFAULT 7,
                is_active BOOLEAN DEFAULT 1,
                is_paid BOOLEAN DEFAULT 0,
                paid_date TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS buddy_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_id INTEGER,
                target_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS buddy_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER,
                user2_id INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                day INTEGER,
                message TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified INTEGER DEFAULT 0
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                achievement_type TEXT,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS support_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                message TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sent_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_text TEXT,
                message_type TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("CREATE INDEX IF NOT EXISTS idx_buddy_requests_target ON buddy_requests(target_id, status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_buddy_requests_requester ON buddy_requests(requester_id, status)")
        
        await db.commit()
        logger.info("Database v6.8 initialized")


async def migrate_database():
    print("\u0417\u0430\u043f\u0443\u0441\u043a \u043c\u0438\u0433\u0440\u0430\u0446\u0438\u0438 \u0431\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445...")
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in await cursor.fetchall()]
        
        if 'paid_date' not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN paid_date TIMESTAMP")
            print("\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0430 \u043a\u043e\u043b\u043e\u043d\u043a\u0430 paid_date")
        
        if 'expires_at' not in [row[1] for row in await (await db.execute("PRAGMA table_info(buddy_requests)")).fetchall()]:
            await db.execute("ALTER TABLE buddy_requests ADD COLUMN expires_at TIMESTAMP")
        
        await db.commit()
    print("\u041c\u0438\u0433\u0440\u0430\u0446\u0438\u044f \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430")


# ====================== \u041e\u0421\u041d\u041e\u0412\u041d\u042b\u0415 \u0424\u0423\u041d\u041a\u0426\u0418\u0418 ======================
async def add_user(user_id: int, username: str = None, full_name: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, current_day) VALUES (?, ?, ?, 1)",
            (user_id, username, full_name)
        )
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return {
                "user_id": row[0], "username": row[1], "full_name": row[2],
                "buddy_id": row[3], "current_day": row[4] or 1,
                "points": row[5] or 0, "timezone": row[6] or 7, "is_paid": row[8] or 0
            }
        return None


async def update_user_current_day(user_id: int, day: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET current_day = ? WHERE user_id = ?", (day, user_id))
        await db.commit()


async def update_user_timezone(user_id: int, timezone: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET timezone = ? WHERE user_id = ?", (timezone, user_id))
        await db.commit()


async def add_points(user_id: int, amount: int, reason: str = ""):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()


# ====================== \u0411\u0410\u0414\u0414\u0418 \u0421\u0418\u0421\u0422\u0415\u041c\u0410 ======================
async def create_buddy_request(requester_id: int, target_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM buddy_requests WHERE requester_id = ? AND target_id = ? AND status = 'pending'",
            (requester_id, target_id)
        )
        if await cursor.fetchone():
            return False
        
        await db.execute(
            "DELETE FROM buddy_requests WHERE requester_id = ? AND target_id = ? AND status IN ('cancelled', 'declined')",
            (requester_id, target_id)
        )
        
        expires_at = (datetime.now() + timedelta(hours=48)).isoformat()
        await db.execute(
            "INSERT INTO buddy_requests (requester_id, target_id, status, expires_at) VALUES (?, ?, 'pending', ?)",
            (requester_id, target_id, expires_at)
        )
        await db.commit()
        return True


async def get_pending_requests_for_user(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """SELECT br.id, br.requester_id, u.username, u.full_name 
              FROM buddy_requests br
              JOIN users u ON br.requester_id = u.user_id
              WHERE br.target_id = ? AND br.status = 'pending' 
              AND br.expires_at > datetime('now')""",
            (user_id,)
        )
        return await cursor.fetchall()


async def accept_buddy_request(request_id: int, target_id: int) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT requester_id FROM buddy_requests WHERE id = ? AND target_id = ? AND status = 'pending'",
            (request_id, target_id)
        )
        row = await cursor.fetchone()
        if not row:
            return {"success": False, "error": "\u0417\u0430\u043f\u0440\u043e\u0441 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d"}
        
        requester_id = row[0]
        
        cursor = await db.execute("SELECT buddy_id FROM users WHERE user_id IN (?, ?)", (requester_id, target_id))
        buddies = await cursor.fetchall()
        if any(b[0] for b in buddies):
            return {"success": False, "error": "\u0423 \u043e\u0434\u043d\u043e\u0433\u043e \u0438\u0437 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439 \u0443\u0436\u0435 \u0435\u0441\u0442\u044c \u0431\u0430\u0434\u0434\u0438"}
        
        await db.execute("UPDATE buddy_requests SET status = 'accepted' WHERE id = ?", (request_id,))
        await db.execute("UPDATE users SET buddy_id = ? WHERE user_id = ?", (target_id, requester_id))
        await db.execute("UPDATE users SET buddy_id = ? WHERE user_id = ?", (requester_id, target_id))
        await db.execute("INSERT INTO buddy_history (user1_id, user2_id) VALUES (?, ?)", (requester_id, target_id))
        await db.commit()
        
        return {"success": True, "requester_id": requester_id}


async def decline_buddy_request(request_id: int, target_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE buddy_requests SET status = 'declined' WHERE id = ? AND target_id = ?",
            (request_id, target_id)
        )
        await db.commit()
        return True


async def cancel_buddy_request(requester_id: int, target_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE buddy_requests SET status = 'cancelled' WHERE requester_id = ? AND target_id = ? AND status = 'pending'",
            (requester_id, target_id)
        )
        await db.commit()
        return True


async def get_active_buddy(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT buddy_id FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None


async def get_buddy(user_id: int):
    return await get_active_buddy(user_id)


async def has_active_buddy(user_id: int) -> bool:
    return await get_active_buddy(user_id) is not None


async def get_daily_buddy_requests_count(user_id: int) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM buddy_requests WHERE requester_id = ? AND created_at > datetime('now', '-1 day')",
            (user_id,)
        )
        return (await cursor.fetchone())[0]


async def get_buddy_history(user_id: int, limit: int = 5):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """SELECT 
                CASE WHEN user1_id = ? THEN user2_id ELSE user1_id END as buddy_id,
                started_at, ended_at
              FROM buddy_history 
              WHERE user1_id = ? OR user2_id = ?
              ORDER BY started_at DESC LIMIT ?""",
            (user_id, user_id, user_id, limit)
        )
        return await cursor.fetchall()


async def get_buddy_username(buddy_id: int) -> str:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT username FROM users WHERE user_id = ?", (buddy_id,))
        row = await cursor.fetchone()
        return row[0] if row and row[0] else f"ID {buddy_id}"


async def get_buddy_days_together(user_id: int) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT MIN(started_at) FROM buddy_history WHERE user1_id = ? OR user2_id = ?", (user_id, user_id))
        row = await cursor.fetchone()
        if row and row[0]:
            created = datetime.fromisoformat(row[0].split(".")[0])
            return max(1, (datetime.now() - created).days)
        return 0


async def get_user_progress(user_id: int):
    user = await get_user(user_id)
    if not user:
        return None
    buddy_days = await get_buddy_days_together(user_id) if user.get("buddy_id") else 0
    return {
        "current_day": user["current_day"],
        "points": user["points"],
        "buddy_id": user["buddy_id"],
        "buddy_days": buddy_days,
        "is_paid": user["is_paid"]
    }


async def set_buddy(requester_id: int, buddy_id: int) -> bool:
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("BEGIN"):
                await db.execute("UPDATE users SET buddy_id = ? WHERE user_id = ?", (buddy_id, requester_id))
                await db.execute("UPDATE users SET buddy_id = ? WHERE user_id = ?", (requester_id, buddy_id))
                await db.execute("INSERT INTO buddy_history (user1_id, user2_id) VALUES (?, ?)", (requester_id, buddy_id))
                await db.commit()
                return True
    except:
        return False


async def break_buddy_pair(user_id: int):
    buddy_id = await get_active_buddy(user_id)
    if not buddy_id:
        return {"success": False, "already_broken": True}
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET buddy_id = NULL WHERE user_id IN (?, ?)", (user_id, buddy_id))
        await db.commit()
    return {"success": True, "buddy_id": buddy_id}


async def get_user_by_username(username: str):
    """\u041d\u0430\u0445\u043e\u0434\u0438\u0442 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u043f\u043e username (case-insensitive). \u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u043e \u0434\u043b\u044f buddy.py"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
            (username,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "user_id": row[0], "username": row[1], "full_name": row[2],
                "buddy_id": row[3], "current_day": row[4] or 1,
                "points": row[5] or 0, "timezone": row[6] or 7, "is_paid": row[8] or 0
            }
        return None


# ====================== \u041e\u0422\u0427\u0401\u0422\u042b ======================
async def save_report(user_id: int, day: int, message: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO reports (user_id, day, message) VALUES (?, ?, ?)",
            (user_id, day, message[:1000])
        )
        await db.commit()


async def create_report(user_id: int, day: int, message: str):
    await save_report(user_id, day, message)


async def mark_report_as_verified(report_id: int, verifier_id: int = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE reports SET verified = 1 WHERE id = ?",
            (report_id,)
        )
        await db.commit()
    return True


async def is_report_verified(report_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT verified FROM reports WHERE id = ?", (report_id,))
        row = await cursor.fetchone()
        return bool(row and row[0] == 1)


# ====================== TRIBUTE / \u041e\u041f\u041b\u0410\u0422\u0410 ======================
async def mark_user_paid(user_id: int):
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "UPDATE users SET is_paid = 1, paid_date = datetime('now') WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
        logger.info(f"\u2705 \u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c {user_id} \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u043e\u043f\u043b\u0430\u0447\u0435\u043d (Tribute)")
        return True
    except Exception as e:
        logger.error(f"\u274c \u041e\u0448\u0438\u0431\u043a\u0430 mark_user_paid \u0434\u043b\u044f {user_id}: {e}")
        return False


async def get_user_paid_status(user_id: int) -> dict:
    user = await get_user(user_id)
    if not user:
        return {"is_paid": False, "paid_date": None}
    return {
        "is_paid": bool(user.get("is_paid", 0)),
        "paid_date": user.get("paid_date")
    }


# ====================== \u0410\u0414\u041c\u0418\u041d \u0424\u0423\u041d\u041a\u0426\u0418\u0418 ======================
async def check_and_award_achievements(user_id: int):
    return True


# ====================== \u0414\u0420\u0423\u0413\u0418\u0415 \u0424\u0423\u041d\u041a\u0426\u0418\u0418 ======================
async def save_support_request(user_id: int, username: str, message: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO support_requests (user_id, username, message) VALUES (?, ?, ?)",
            (user_id, username, message[:2000])
        )
        await db.commit()


async def save_message(user_id: int, message_text: str, message_type: str = "general"):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO sent_messages (user_id, message_text, message_type) VALUES (?, ?, ?)",
            (user_id, message_text[:500], message_type)
        )
        await db.commit()


async def get_rating_report(limit: int = 20):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, full_name, points, current_day, is_paid
            FROM users 
            WHERE is_active = 1
            ORDER BY points DESC, current_day DESC
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()


print("\u2705 database.py updated for Detox_30_Bot_Refactored (added get_user_by_username + fixed import for src.config.settings)")