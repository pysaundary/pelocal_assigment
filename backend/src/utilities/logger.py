# app/utils/logger.py
import logging
import sys
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class LoggerConfig:
    """
        name (str): Logger name.
        level (int): Logging level.
        console (bool): Enable console output.
        file_path (str): Path to log file.
        rotate_when (str|None): Time interval specifier for time-based rotation
            (e.g. 'midnight', 'H', 'D', 'W0'). Set to None to disable.
        rotate_interval (int): Number of units for time-based rotation.
        max_bytes (int): Max size in bytes for size-based rotation.
        backup_count (int): Number of old files to keep.
        fmt (str): Log message format.
    """
    def __init__(
        self,
        name: str = "app",
        level: int = logging.INFO,
        console: bool = True,
        file_path: str = "logs/app.log",
        rotate_when: str | None = "D",
        rotate_interval: int = 10,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 7,
        fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ):
        self.name = name
        self.level = level
        self.console = console
        self.file_path = file_path
        self.rotate_when = rotate_when
        self.rotate_interval = rotate_interval
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.fmt = fmt

class LoggerFactory:
    """
    Factory for creating a configured logger with optional console,
    size-based rotation, and/or time-based rotation.
    """
    def __init__(self, config: LoggerConfig):
        self.config = config
        self.logger = logging.getLogger(config.name)
        self._configure()

    def _configure(self):
        cfg = self.config
        # Avoid reconfiguration
        if self.logger.hasHandlers():
            return

        self.logger.setLevel(cfg.level)
        formatter = logging.Formatter(cfg.fmt)

        # Console handler
        if cfg.console:
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(cfg.level)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        # Ensure log directory exists
        log_dir = os.path.dirname(cfg.file_path) or "."
        os.makedirs(log_dir, exist_ok=True)

        # File handler: choose time-based or size-based rotation
        if cfg.rotate_when:
            # Time-based rotating file handler
            fh = TimedRotatingFileHandler(
                filename=cfg.file_path,
                when=cfg.rotate_when,
                interval=cfg.rotate_interval,
                backupCount=cfg.backup_count,
                encoding="utf-8",
                utc=False
            )
        else:
            # Size-based rotating file handler
            fh = RotatingFileHandler(
                filename=cfg.file_path,
                maxBytes=cfg.max_bytes,
                backupCount=cfg.backup_count,
                encoding="utf-8"
            )

        fh.setLevel(cfg.level)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get_logger(self) -> logging.Logger:
        return self.logger
