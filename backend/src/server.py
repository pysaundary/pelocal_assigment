from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database.sqllite.connector import migrate_db 
from src.utilities.the_object_collector import TheObjectCollector
import traceback
from uvicorn import Config, Server

@asynccontextmanager
async def lifespan(app: FastAPI):
    collector = TheObjectCollector()
    logger = collector.getKey("api_logger")
    try:
        config = collector.getKey("config",logger=logger)
        db_path = config.get("db_url")
        await migrate_db(db_path,logger)
    except Exception as e:
        logger.critical(traceback.format_exc())
        logger.error(f"failed due to {e}")
    yield
def create_app():
    app = FastAPI(lifespan=lifespan)    
    return app

async def run_server():
    collector = TheObjectCollector()
    logger = collector.getKey("api_logger")
    try:
        app = create_app()
        config = collector.getKey("config",logger=logger)
        server = Server(
            config=Config(
        app=app,
        host=config.get("host"),
        port=int(config.get("backend_port")), 
    )
        )
        await server.serve()
    except Exception as e:
        logger.critical(traceback.format_exc())
        logger.error("failed due to {e}")