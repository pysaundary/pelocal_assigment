from slugify import slugify
import aiosqlite

async def generate_slug_with_id(title: str, db: aiosqlite.Connection) -> str:
    """
    Use existing async connection (from dependency) and raw SQL:
    slug = slugify(title[:20]) + '-' + (MAX(id)+1)
    """
    base_part = slugify(title[:20])
    cursor = await db.execute("SELECT MAX(id) FROM users")
    row = await cursor.fetchone()
    await cursor.close()

    max_id = row[0] if row and row[0] is not None else 0
    new_id = max_id + 1
    return f"{base_part}-{new_id}"

async def email_exists(email: str, db: aiosqlite.Connection) -> bool:
    sql = "SELECT 1 FROM users WHERE email = ? LIMIT 1"
    cur = await db.execute(sql, (email,))
    row = await cur.fetchone()
    await cur.close()
    return row is not None 

async def username_exists(username: str, db: aiosqlite.Connection) -> bool:
    sql = "SELECT 1 FROM users WHERE username = ? LIMIT 1"
    cur = await db.execute(sql, (username,))
    row = await cur.fetchone()
    await cur.close()
    return row is not None  # presence check [web:146][web:148]

async def create_username_from_email(email: str, db: aiosqlite.Connection) -> str:
    """
    Username = email.split('@')[0]
    If taken, try username_{MAX(id)+1} and keep incrementing until unique.
    """
    base_username = email.split("@", 1)[0]

    # If base is available, use it
    if not await username_exists(base_username, db):
        return base_username

    # Get latest user id (DESC LIMIT 1 or MAX(id))
    cur = await db.execute("SELECT MAX(id) FROM users")
    row = await cur.fetchone()
    await cur.close()
    latest_id = row[0] if row and row[0] is not None else 0
    if latest_id <= 0:
        latest_id = 1

    # Try base_{n} until unique
    n = latest_id
    while True:
        candidate = f"{base_username}_{n}"
        if not await username_exists(candidate, db):
            return candidate
        n += 1

async def email_exists(email: str, db: aiosqlite.Connection) -> bool:
    sql = "SELECT 1 FROM users WHERE email = ? LIMIT 1"
    cursor = await db.execute(sql, (email,))
    row = await cursor.fetchone()
    await cursor.close()
    return row is not None