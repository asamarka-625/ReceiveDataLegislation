# Внешние зависимости
from dataclasses import dataclass, field
from dotenv import load_dotenv
import os
import logging
# Внутренние модули
from app.logger import setup_logger


load_dotenv()


@dataclass
class Config:
    _database_outer_url: str = field(default_factory=lambda: os.getenv("DATABASE_OUTER_URL"))
    _database_inner_url: str = field(default_factory=lambda: os.getenv("DATABASE_INNER_URL"))
    logger: logging.Logger = field(init=False)

    CONTROLLER: str = field(default_factory=lambda: os.getenv("CONTROLLER"))
    UNLOADED_DATA: str = field(init=False)

    LIMIT_DB_DATA: int = field(default_factory=lambda: int(os.getenv("LIMIT_DB_DATA")))

    def __post_init__(self):
        self.logger = setup_logger(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_dir=os.getenv("LOG_DIR", "logs"),
            log_file=os.getenv("LOG_FILE", "parser_log")
        )

        self.UNLOADED_DATA: str = f"{self.CONTROLLER}/api/v1/db/unloaded"

        self.validate()
        self.logger.info("Configuration initialized")

    # Валидация конфигурации
    def validate(self):
        if not self._database_outer_url:
            self.logger.critical("DATABASE_OUTER_URL is required in environment variables")
            raise ValueError("DATABASE_OUTER_URL is required")

        if not self._database_inner_url:
            self.logger.critical("DATABASE_INNER_URL is required in environment variables")
            raise ValueError("DATABASE_INNER_URL is required")

        self.logger.debug("Configuration validation passed")

    @property
    def DATABASE_OUTER_URL(self) -> str:
        return self._database_outer_url

    @property
    def DATABASE_INNER_URL(self) -> str:
        return self._database_inner_url

    def __str__(self) -> str:
        return f"""
        Config(database_outer={self._database_outer_url}, 
        database_inner={self._database_inner_url}, 
        log_level={self.logger.level})
        """


_instance = None


def get_config() -> Config:
    global _instance
    if _instance is None:
        _instance = Config()

    return _instance