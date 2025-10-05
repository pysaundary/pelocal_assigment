from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database.sqllite.connector import migrate_db 
from src.utilities.the_object_collector import TheObjectCollector
from src.controller.authentication import auth_apis
from src.controller.task import task_router
import traceback
from uvicorn import Config, Server
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

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

FRONTEND_DIR = "todo-frontend" 

def create_app(the_collector):
    app = FastAPI(lifespan=lifespan)

    app.include_router(auth_apis)
    app.include_router(task_router)

    base_dir = the_collector.getKey("base_dir")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=f"{base_dir}/{FRONTEND_DIR}", html=False), name="static")

    @app.get("/", include_in_schema=False)
    async def root_index():
        return FileResponse(f"{base_dir}/{FRONTEND_DIR}/index.html")

    @app.get("/tasks", include_in_schema=False)
    async def tasks_page():
        return FileResponse(f"{base_dir}/{FRONTEND_DIR}/tasks.html")

    return app


async def run_server():
    collector = TheObjectCollector()
    logger = collector.getKey("api_logger")
    try:
        app = create_app(collector)
        @app.get("/", include_in_schema=False)
        async def root_index():
            return FileResponse(f"static/todo-frontend/index.html")
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