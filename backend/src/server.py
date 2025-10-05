from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from uvicorn import Config, Server
import os
from src.database.sqllite.connector import migrate_db
from src.utilities.the_object_collector import TheObjectCollector
from src.controller.authentication import auth_apis
from src.controller.task import task_router
import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    collector = TheObjectCollector()
    logger = collector.getKey("api_logger")
    try:
        config = collector.getKey("config", logger=logger)
        db_path = config.get("db_url")
        await migrate_db(db_path, logger)
    except Exception:
        logger.critical(traceback.format_exc())
    yield

def create_app():
    collector = TheObjectCollector()
    app = FastAPI(lifespan=lifespan)

    # APIs
    app.include_router(auth_apis)
    app.include_router(task_router)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount backend/static at /static
    static_dir = f"{collector.getKey('base_dir')}/backend/static"
    app.mount("/static", StaticFiles(directory=os.path.join(collector.getKey('base_dir'),"backend", "static")), name="static")

    # Serve HTML pages
    @app.get("/", include_in_schema=False)
    async def root_index():
        return FileResponse(f"{static_dir}/index.html")

    @app.get("/tasks", include_in_schema=False)
    async def tasks_page():
        return FileResponse(f"{static_dir}/tasks.html")

    return app

async def run_server():
    collector = TheObjectCollector()
    logger = collector.getKey("api_logger")
    try:
        app = create_app()
        cfg = collector.getKey("config", logger=logger)
        server = Server(config=Config(app=app, host=cfg.get("host"), port=int(cfg.get("backend_port"))))
        await server.serve()
    except Exception:
        logger.critical(traceback.format_exc())
