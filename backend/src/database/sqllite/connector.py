from src.database.sqllite.migration_file import MIGRATION_SCRIPT
import aiosqlite
import traceback

async def migrate_db(url: str, logger=None):
    db_path = url.replace("sqlite:///", "")
    try:
        async with aiosqlite.connect(db_path) as conn:
            await conn.executescript(MIGRATION_SCRIPT[-1])
            await conn.commit()     
            if logger:
                logger.info(f"Migration script executed successfully on {url}")                
    except Exception as e:
        if logger:
            logger.critical(traceback.format_exc())
            logger.error(f"Failed to connect with database due to {e}")
        raise

async def get_async_db(db : str = "todo.db" ):
    async with aiosqlite.connect(db) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def get_async_db_conn():
    db_path = "todo.db"  # read from env/config internally
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        yield conn