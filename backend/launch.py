import os
import asyncio
from dotenv import load_dotenv

from src.utilities.logger import LoggerFactory, LoggerConfig
from src.utilities.the_object_collector import TheObjectCollector
from src.server import run_server
class LetsStartTheCode:
    """
    init hai bs aur kuch nhi
    """

    def __init__(self, *, base_dir: str | None = None):
        self.base_dir = base_dir or os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir, os.pardir, os.pardir, os.pardir
            )
        )
        env_path = os.path.join(self.base_dir, ".env")
        load_dotenv(env_path)
        self._validate_env()
        self.logs_dir = os.path.join(self.base_dir,"backend", "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        log_file = os.path.join(self.logs_dir, "server.log")
        server_cfg = LoggerConfig(
            name="server",
            console=False,
            file_path=log_file,
            rotate_when="D",           
            rotate_interval=3,         
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "7"))
        )
        self.logger = LoggerFactory(server_cfg).get_logger()
        self.collector = TheObjectCollector(logger=self.logger)
        self.logger.info("─" * 100)
        self.logger.info(" Server started with configuration:")
        self.logger.info(f"    • BASE_DIR    = {self.base_dir}")
        self.logger.info(f"    • ENV_PATH    = {env_path}")
        self.logger.info(f"    • LOG_FILE    = {log_file}")
        self.logger.info("─" * 100)

    def _validate_env(self):
        """Fail early if required env vars missing."""
        required = ["SECRET_KEY", "HOST", "BACK_END_PORT", "FRONT_END_PORT", "SQLLITE_URL","ALGO"]
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    async def _launch_code(self) -> None:
        """ this is start point """
        # API logger
        api_log_dir = os.path.join(self.logs_dir, "api_logs")
        os.makedirs(api_log_dir, exist_ok=True)
        api_cfg = LoggerConfig(
            name="api_logger",
            console=False,
            file_path=os.path.join(api_log_dir, "api.log"),
            rotate_when=None,           # size-based rotation
            max_bytes=5 * 1024 * 1024,  # 5 MB
            backup_count=3
        )
        api_logger = LoggerFactory(api_cfg).get_logger()
        self.collector.addOrUpdate("api_logger", api_logger, api_logger)
        self.collector.addOrUpdate("base_dir",self.base_dir)
        # Store useful config in collector
        config_data = {
            "secret_key": os.getenv("SECRET_KEY"),
            "algo":os.getenv("ALGO"),
            "host": os.getenv("HOST"),
            "backend_port": os.getenv("BACK_END_PORT"),
            "frontend_port": os.getenv("FRONT_END_PORT"),
            "db_url": os.getenv("SQLLITE_URL"),
        }
        self.collector.addOrUpdate("config", config_data, self.logger)

        self.logger.info("Launch sequence complete. Collector populated.")
        fastServer = asyncio.create_task(
                run_server(), name="Fast Apis"
            )


    def run(self):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop) 
            loop.create_task(self._launch_code())
            loop.run_forever()
        finally:
            loop.stop()
            pending = asyncio.all_tasks(loop=loop)
            for t in pending:
                t.cancel()
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.close()



if __name__ == "__main__":
    # Allow optional override of BASE_DIR via env
    base_dir = os.getcwd()
    app = LetsStartTheCode(base_dir=os.path.join(base_dir))
    app.run()
