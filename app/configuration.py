"""
Configuration file.
"""
__all__ = ["config", "logger", ]

import sys
from dataclasses import dataclass, field
from os import getenv
from typing import Literal

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


@dataclass
class Paths:
    """
    Contains configuration parametrs about paths.
    """
    LOGS_FOLDER_PATH: str = "logs"


@dataclass
class Configuration:
    """
    All in one configuration dataclass.
    """
    VERSION: float = 1.00

    # std logs level
    STD_LOGGER_LEVEL: Literal["DEBUG", "INFO", "ERROR"] | int = "DEBUG"

    # files logs level
    FILE_LOGGER_LEVEL: Literal["DEBUG", "INFO", "ERROR"] | int = "DEBUG"

    # paths configurations
    paths: Paths = field(default_factory=Paths)

    # server ip
    SERVER_HOST: str = getenv("SERVER_HOST", "localhost")

    # server post
    SERVER_PORT: int = int(getenv("SERVER_PORT", "8000"))

    # master server ip
    MASTER_SERVER_HOST: str = getenv("MASTER_SERVER_HOST")

    # master server port
    MASTER_SERVER_PORT: int = int(getenv("MASTER_SERVER_PORT", "80"))

    # admin panel login
    ADMIN_USERNAME: str = getenv("ADMIN_USERNAME", "username")

    # admin panel password
    ADMIN_PASSWORD: str = getenv("ADMIN_PASSWORD", "password")

    # admin panel logo url
    ADMIN_LOGO_URL: str = "https://cdn0.iconfinder.com/data/icons/phosphor-duotone-vol-3/256/robot-duotone-512.png"

    # admin panel cypher key
    CYPHER_KEY: str = getenv("CYPHER_KEY", "cypher_key")

    # databaste path
    DATABASE_URL: str = getenv("DATABASE_URL", "sqlite:///database.db")

    # interval to update balance
    BALANCE_UPDATE_INTERVAL: int | float = 1

    # interval to notify master-server about current balance
    BALANCE_NOTIFY_INTERVAL: int | float = 60

    # interval to fetch orders and positions from trader and user accounts
    TRADER_POLLING_INTERVAL: int | float = 10

    def __post_init__(self) -> None:
        assert self.MASTER_SERVER_HOST, "Master server host and port are required!"


config = Configuration()

# Set up logging
logger.remove()
for level in ["ERROR", "INFO", "DEBUG"]:
    logger.add(f'{config.paths.LOGS_FOLDER_PATH}/{level.lower()}.log', level=level,
               format="<white>{time: %d.%m %H:%M:%S.%f}</white> | "
                      "<level>{level}</level>| "
                      "|{name} {function} line:{line}| "
                      "<bold>{message}</bold>",
               rotation="5 MB",
               compression='zip')
logger.add(sys.stderr, level=config.STD_LOGGER_LEVEL,
           format="<white>{time: %d.%m %H:%M:%S}</white>|"
                  "<level>{level}</level>|"
                  "<bold>{message}</bold>")
