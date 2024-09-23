from app.api.models import UserSettings, TraderSettings
from app.database import Keys

from app.configuration import logger
from .abstract import AbstractServiceManager


class UnifiedServiceManager(AbstractServiceManager):

    @classmethod
    def on_user_settings_update(cls, u: UserSettings) -> None:
        logger.info(f"User settings update: {u}")

    @classmethod
    def on_trader_settings_update(cls, u: TraderSettings) -> None:
        logger.info(f"Trader settings update: {u}")

    @classmethod
    def on_api_keys_update(cls, u: Keys) -> None:
        logger.info(f"Api keys update: {u}")

    @classmethod
    def run_tasks(cls) -> None:
        pass
