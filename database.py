import aiosqlite
import logging
from config import DATABASE_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def initialize_db():
    """Initializes the database and creates tables if they don't exist."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                keyword TEXT NOT NULL,
                UNIQUE(user_id, keyword)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                company TEXT,
                link TEXT NOT NULL,
                source TEXT NOT NULL
            )
        """)
        await db.commit()
    logger.info("Database initialized successfully.")

async def add_subscription(user_id: int, keyword: str):
    """Adds a new keyword subscription for a user."""
    keyword = keyword.lower().strip()
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "INSERT INTO subscriptions (user_id, keyword) VALUES (?, ?)",
                (user_id, keyword)
            )
            await db.commit()
        logger.info(f"User {user_id} subscribed to '{keyword}'")
        return True
    except aiosqlite.IntegrityError:
        logger.warning(f"User {user_id} is already subscribed to '{keyword}'")
        return False

async def remove_subscription(user_id: int, keyword: str):
    """Removes a keyword subscription for a user."""
    keyword = keyword.lower().strip()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM subscriptions WHERE user_id = ? AND keyword = ?",
            (user_id, keyword)
        )
        await db.commit()
        if cursor.rowcount > 0:
            logger.info(f"User {user_id} unsubscribed from '{keyword}'")
            return True
        logger.warning(f"User {user_id} tried to unsubscribe from a non-existent keyword '{keyword}'")
        return False

async def get_subscriptions(user_id: int):
    """Retrieves all keyword subscriptions for a user."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT keyword FROM subscriptions WHERE user_id = ?", (user_id,))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def get_all_subscriptions():
    """Retrieves all subscriptions grouped by keyword."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT keyword, user_id FROM subscriptions")
        rows = await cursor.fetchall()
        subscriptions = {}
        for keyword, user_id in rows:
            if keyword not in subscriptions:
                subscriptions[keyword] = []
            subscriptions[keyword].append(user_id)
        return subscriptions

async def is_job_posted(job_id: str):
    """Checks if a job has already been posted by its unique ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
        return await cursor.fetchone() is not None

async def add_posted_job(job_id: str, title: str, company: str, link: str, source: str):
    """Adds a record of a posted job to prevent duplicates."""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "INSERT INTO jobs (job_id, title, company, link, source) VALUES (?, ?, ?, ?, ?)",
                (job_id, title, company, link, source)
            )
            await db.commit()
    except aiosqlite.IntegrityError:
        logger.warning(f"Attempted to add a duplicate job with ID: {job_id}")


async def get_all_unique_keywords():
    """Retrieves a list of all unique keywords from the subscriptions table."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT DISTINCT keyword FROM subscriptions")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]