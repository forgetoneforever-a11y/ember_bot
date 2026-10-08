import asyncpg
from config import DATABASE_URL

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            name TEXT NOT NULL,
            age INT NOT NULL,
            gender TEXT NOT NULL,
            looking_for TEXT NOT NULL,
            city TEXT NOT NULL,
            bio TEXT NOT NULL,
            photo_id TEXT NOT NULL,
            views INT DEFAULT 0,
            likes_received INT DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS likes (
            from_id BIGINT,
            to_id BIGINT,
            created_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (from_id, to_id)
        );

        CREATE TABLE IF NOT EXISTS matches (
            user1 BIGINT,
            user2 BIGINT,
            created_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (user1, user2)
        );

        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            from_id BIGINT,
            to_id BIGINT,
            reason TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

async def user_exists(user_id: int) -> bool:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM users WHERE user_id=$1", user_id)
        return row is not None

async def create_user(data: dict):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users(user_id, username, name, age, gender,
                              looking_for, city, bio, photo_id)
            VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)
        """, data["user_id"], data["username"], data["name"], data["age"],
             data["gender"], data["looking_for"], data["city"],
             data["bio"], data["photo_id"])

async def get_user(user_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)

async def get_next_profile(user_id: int):
    """Возвращает следующую анкету для показа."""
    async with pool.acquire() as conn:
        me = await conn.fetchrow("SELECT gender, looking_for, city FROM users WHERE user_id=$1", user_id)
        if not me:
            return None
        # пол собеседника должен совпадать с looking_for
        want_gender = me["looking_for"]
        # моя анкета должна подходить под его looking_for
        my_gender = me["gender"]
        row = await conn.fetchrow("""
            SELECT * FROM users
            WHERE is_active=TRUE
              AND user_id != $1
              AND gender = $2
              AND looking_for = $3
              AND user_id NOT IN (SELECT to_id FROM likes WHERE from_id=$1)
            ORDER BY RANDOM() LIMIT 1
        """, user_id, want_gender, my_gender)
        return row

async def add_like(from_id: int, to_id: int) -> bool:
    """Возвращает True если это взаимный лайк (мэтч)."""
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO likes(from_id, to_id) VALUES($1,$2) ON CONFLICT DO NOTHING",
                           from_id, to_id)
        await conn.execute("UPDATE users SET likes_received = likes_received + 1 WHERE user_id=$1", to_id)
        row = await conn.fetchrow("SELECT 1 FROM likes WHERE from_id=$1 AND to_id=$2", to_id, from_id)
        if row:
            u1, u2 = sorted([from_id, to_id])
            await conn.execute("INSERT INTO matches(user1, user2) VALUES($1,$2) ON CONFLICT DO NOTHING", u1, u2)
            return True
        return False

async def add_view(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET views = views + 1 WHERE user_id=$1", user_id)

async def report_user(from_id: int, to_id: int, reason: str):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO reports(from_id, to_id, reason) VALUES($1,$2,$3)",
                           from_id, to_id, reason)

async def deactivate_user(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET is_active=FALSE WHERE user_id=$1", user_id)

# --- для API админки ---
async def get_all_users():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(r) for r in rows]

async def get_stats():
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        active = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_active=TRUE")
        likes = await conn.fetchval("SELECT COUNT(*) FROM likes")
        matches = await conn.fetchval("SELECT COUNT(*) FROM matches")
        reports = await conn.fetchval("SELECT COUNT(*) FROM reports")
        return {"total": total, "active": active, "likes": likes,
                "matches": matches, "reports": reports}

async def get_top_users(limit: int = 10):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, name, username, age, city, views, likes_received, photo_id
            FROM users
            ORDER BY (likes_received * 2 + views) DESC
            LIMIT $1
        """, limit)
        return [dict(r) for r in rows]